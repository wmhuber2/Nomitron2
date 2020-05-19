from git import Repo
import shutil, os, sys

if __name__ == "__main__":
    rw_dir = 'https://github.com/wmhuber2/Nomitron2'
    dir = os.getcwd()

    while 1:
        tmpdir = os.path.join(dir,'tmp')
        try:
            shutil.rmtree(tmpdir)
        except:
            print('No TMP folder. Resuming...')
        os.mkdir(tmpdir)
    
        Repo.clone_from(rw_dir, tmpdir)

        root_src_dir = tmpdir
        root_dst_dir = dir

        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    # in case of the src and dst are the same file
                    if os.path.samefile(src_file, dst_file):
                        continue
                    os.remove(dst_file)

                shutil.move(src_file, dst_dir)
        os.system('python'+str(sys.version_info.major) + '.' +str(sys.version_info.minor) + ' '+os.path.join(dir,'DiscordBot.py') + " 2>&1 | tee -a nomitron_log.txt")















