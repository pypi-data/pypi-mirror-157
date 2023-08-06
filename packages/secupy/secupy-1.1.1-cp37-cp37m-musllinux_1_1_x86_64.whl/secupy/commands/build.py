import itertools
import multiprocessing.pool
import os
from pathlib import Path

import secupy
import tqdm


def walk_tree(
    srcroot: Path,
    destroot: Path,
    excludes: list,
    includes: list,
    unprotect: list,
    cryptor: secupy.SecupyCryptoUtil,
    debug: bool,
):

    srcroot_is_file = srcroot.is_file()

    def files_worker(root: Path, f: Path):
        if srcroot_is_file:
            outroot = destroot
        else:
            outroot = destroot / root.relative_to(srcroot)

        inf = root / f

        if inf in excludes:
            outf = outroot / f
            if debug:
                print(f'Ignore file "{inf}" -> "{outf}"')
            if inf in includes:
                outf = outroot / f
                outf.parent.mkdir(parents=True, exist_ok=True)
                outf.write_bytes(inf.read_bytes())
                if debug:
                    print(f'Copy file "{inf}" -> "{outf}"')
        elif f.suffix in (".py", ".pyw", ".pyc"):
            if inf in unprotect:
                outf = outroot / f
                outf.parent.mkdir(parents=True, exist_ok=True)
                outf.write_bytes(inf.read_bytes())
                if debug:
                    print(f'Copy file "{inf}" -> "{outf}"')
            else:
                f_enc = f.stem + cryptor.ext
                outf = outroot / f_enc
                outf.parent.mkdir(parents=True, exist_ok=True)
                cryptor.encrypt_file(str(inf), str(outf))
                if debug:
                    print(f'Encrypt "{inf}" -> "{outf}"')
        else:
            outf = outroot / f
            outf.parent.mkdir(parents=True, exist_ok=True)
            outf.write_bytes(inf.read_bytes())
            if debug:
                print(f'Copy file "{inf}" -> "{outf}"')

    def ifiles_worker(args):
        files_worker(*args)

    def dirs_worker(root: Path, d: Path):
        outroot = destroot / root.relative_to(srcroot)
        ind = root / d
        outd = outroot / d

        if ind in excludes:
            if debug:
                print(f'Exclude dir "{ind}"')
            if ind in includes:
                outd.mkdir(parents=True, exist_ok=True)
                if debug:
                    print(f'Make dir "{outd}"')
        else:
            outd.mkdir(parents=True, exist_ok=True)
            if debug:
                print(f'Make dir "{outd}"')

    def idirs_worker(args):
        dirs_worker(*args)

    total = 0
    walked = []

    if srcroot_is_file:
        dirs, files = (), (srcroot.name,)
        total += len(dirs) + len(files)
        walked.append((srcroot.parent, dirs, files))
    else:
        for root, dirs, files in os.walk(srcroot):
            total += len(dirs) + len(files)
            walked.append((root, dirs, files))

    destroot.mkdir(parents=True, exist_ok=True)

    with tqdm.tqdm(unit="file", total=total, ncols=80, disable=debug) as pb:

        # fmt: off
        dirs = itertools.chain.from_iterable(
            ((Path(_root), Path(d),) for d in _dirs) for _root, _dirs, _files in walked
        )
        # fmt:on

        # fmt: off
        files = itertools.chain.from_iterable(
            ((Path(_root), Path(f),) for f in _files) for _root, _dirs, _files in walked
        )
        # fmt:on

        w = cryptor.cpu
        with multiprocessing.pool.ThreadPool(w) as pool:
            [pb.update() for _ in pool.imap_unordered(idirs_worker, dirs, w)]
            [pb.update() for _ in pool.imap_unordered(ifiles_worker, files, w)]


def main(args):
    srcroot = Path(args.source).resolve().absolute()
    destroot = Path(args.destination).resolve().absolute()

    if not srcroot.exists():
        raise OSError(f"Source: Not found: {srcroot}")

    excludes = []
    if args.exclude and srcroot.is_dir():
        for e in args.exclude:
            for f in srcroot.glob(e):
                if f.is_dir():
                    excludes += [f]
                    excludes += f.glob("*")
                elif f.is_file():
                    excludes += [f]

    includes = []
    if args.include and srcroot.is_dir():
        for i in args.include:
            for f in srcroot.glob(i):
                if f.is_dir():
                    includes += [f]
                    includes += f.glob("*")
                elif f.is_file():
                    includes += [f]

    unprotects = []
    if args.unprotect and srcroot.is_dir():
        for u in args.unprotect:
            for f in srcroot.glob(u):
                if f.is_dir():
                    unprotects += [f]
                    unprotects += f.glob("*")
                elif f.is_file():
                    unprotects += [f]

    ttl = args.ttl
    password = args.password
    salt = args.salt
    debug = args.verbose

    cryptor = secupy.SecupyCryptoUtil(
        debug=debug, ttl=ttl, password=password, salt=salt
    )

    walk_tree(srcroot, destroot, excludes, includes, unprotects, cryptor, debug)
