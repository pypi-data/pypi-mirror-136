import os

from conans.cli.commands import make_abs_path
from conans.cli.formatters.graph import print_graph_basic, print_graph_packages
from conans.cli.command import conan_command, Extender, COMMAND_GROUPS, OnceArgument
from conans.cli.common import _add_common_install_arguments, _help_build_policies, \
    get_profiles_from_args, get_lockfile, get_multiple_remotes
from conans.cli.output import ConanOutput
from conans.client.graph.printer import print_graph
from conans.errors import ConanException
from conans.model.recipe_ref import RecipeReference


def _get_conanfile_path(path, cwd, py):
    """
    param py= True: Must be .py, False: Must be .txt, None: Try .py, then .txt
    """
    candidate_paths = list()
    path = make_abs_path(path, cwd)

    if os.path.isdir(path):  # Can be a folder
        if py:
            path = os.path.join(path, "conanfile.py")
            candidate_paths.append(path)
        elif py is False:
            path = os.path.join(path, "conanfile.txt")
            candidate_paths.append(path)
        else:
            path_py = os.path.join(path, "conanfile.py")
            candidate_paths.append(path_py)
            if os.path.exists(path_py):
                path = path_py
            else:
                path = os.path.join(path, "conanfile.txt")
                candidate_paths.append(path)
    else:
        candidate_paths.append(path)

    if not os.path.isfile(path):  # Must exist
        raise ConanException("Conanfile not found at %s" % " or ".join(candidate_paths))

    if py and not path.endswith(".py"):
        raise ConanException("A conanfile.py is needed, " + path + " is not acceptable")

    return path


def graph_compute(args, conan_api, strict_lockfile=True):
    cwd = os.getcwd()
    lockfile_path = make_abs_path(args.lockfile, cwd)
    path = _get_conanfile_path(args.path, cwd, py=None) if args.path else None
    reference = RecipeReference.loads(args.reference) if args.reference else None
    if not path and not reference:
        raise ConanException("Please specify at least a path to a conanfile or a valid reference.")

    # Basic collaborators, remotes, lockfile, profiles
    remotes = get_multiple_remotes(conan_api, args.remote)
    lockfile = get_lockfile(lockfile=lockfile_path, strict=strict_lockfile)
    profile_host, profile_build = get_profiles_from_args(conan_api, args)
    root_ref = RecipeReference(name=args.name, version=args.version,
                               user=args.user, channel=args.channel)

    out = ConanOutput()
    out.highlight("-------- Input profiles ----------")
    out.info("Profile host:")
    out.info(profile_host.dumps())
    out.info("Profile build:")
    out.info(profile_build.dumps())

    # decoupling the most complex part, which is loading the root_node, this is the point where
    # the difference between "reference", "path", etc
    root_node = conan_api.graph.load_root_node(reference, path, profile_host, profile_build,
                                               lockfile, root_ref,
                                               create_reference=None,
                                               is_build_require=args.build_require,
                                               require_overrides=args.require_override,
                                               remotes=remotes,
                                               update=args.update)

    out.highlight("-------- Computing dependency graph ----------")
    check_updates = args.check_updates if "check_updates" in args else False
    deps_graph = conan_api.graph.load_graph(root_node, profile_host=profile_host,
                                            profile_build=profile_build,
                                            lockfile=lockfile,
                                            remotes=remotes,
                                            update=args.update,
                                            check_update=check_updates)
    print_graph_basic(deps_graph)
    out.highlight("\n-------- Computing necessary packages ----------")
    conan_api.graph.analyze_binaries(deps_graph, args.build, remotes=remotes, update=args.update)
    print_graph_packages(deps_graph)

    return deps_graph, lockfile


def common_graph_args(subparser):
    subparser.add_argument("path", nargs="?",
                           help="Path to a folder containing a recipe (conanfile.py "
                                "or conanfile.txt) or to a recipe file. e.g., "
                                "./my_project/conanfile.txt.")
    subparser.add_argument("--name", action=OnceArgument,
                           help='Provide a package name if not specified in conanfile')
    subparser.add_argument("--version", action=OnceArgument,
                           help='Provide a package version if not specified in conanfile')
    subparser.add_argument("--user", action=OnceArgument,
                           help='Provide a user')
    subparser.add_argument("--channel", action=OnceArgument,
                           help='Provide a channel')

    subparser.add_argument("--reference", action=OnceArgument,
                           help='Provide a package reference instead of a conanfile')

    _add_common_install_arguments(subparser, build_help=_help_build_policies.format("never"))
    subparser.add_argument("--build-require", action='store_true', default=False,
                           help='The provided reference is a build-require')
    subparser.add_argument("--require-override", action="append",
                           help="Define a requirement override")


@conan_command(group=COMMAND_GROUPS['consumer'])
def install(conan_api, parser, *args):
    """
    Installs the requirements specified in a recipe (conanfile.py or conanfile.txt).

    It can also be used to install a concrete package specifying a
    reference. If any requirement is not found in the local cache, it will
    retrieve the recipe from a remote, looking for it sequentially in the
    configured remotes. When the recipes have been downloaded it will try
    to download a binary package matching the specified settings, only from
    the remote from which the recipe was retrieved. If no binary package is
    found, it can be built from sources using the '--build' option. When
    the package is installed, Conan will write the files for the specified
    generators.
    """
    common_graph_args(parser)
    parser.add_argument("-g", "--generator", nargs=1, action=Extender,
                        help='Generators to use')
    parser.add_argument("-if", "--install-folder", action=OnceArgument,
                        help='Use this directory as the directory where to put the generator'
                             'files.')
    parser.add_argument("-of", "--output-folder",
                        help='The root output folder for generated and build files')
    parser.add_argument("-sf", "--source-folder", help='The root source folder')
    parser.add_argument("--no-imports", action='store_true', default=False,
                        help='Install specified packages but avoid running imports')

    args = parser.parse_args(*args)

    # parameter validation
    if args.reference and (args.name or args.version or args.user or args.channel):
        raise ConanException("Can't use --name, --version, --user or --channel arguments with "
                             "--reference")

    cwd = os.getcwd()
    install_folder = make_abs_path(args.install_folder or "", cwd)
    path = _get_conanfile_path(args.path, cwd, py=None) if args.path else None
    conanfile_folder = os.path.dirname(path) if path else None
    reference = RecipeReference.loads(args.reference) if args.reference else None

    remote = get_multiple_remotes(conan_api, args.remote)

    deps_graph, lockfile = graph_compute(args, conan_api)

    out = ConanOutput()
    out.highlight("\n-------- Installing packages ----------")
    conan_api.install.install_binaries(deps_graph=deps_graph, build_modes=args.build,
                                       remotes=remote, update=args.update)
    out.highlight("\n-------- Finalizing install (imports, deploy, generators) ----------")
    conan_api.install.install_consumer(deps_graph=deps_graph, base_folder=cwd, reference=reference,
                                       install_folder=install_folder, generators=args.generator,
                                       no_imports=args.no_imports, conanfile_folder=conanfile_folder,
                                       source_folder=args.source_folder,
                                       output_folder=args.output_folder
                                       )
    if args.lockfile_out:
        lockfile_out = make_abs_path(args.lockfile_out, cwd)
        out.info(f"Saving lockfile: {lockfile_out}")
        lockfile.save(lockfile_out)
