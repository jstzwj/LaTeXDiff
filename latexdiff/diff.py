
import argparse
import re
import os
import tempfile
import subprocess
import time
import sys


def read_tex(path: str) -> str:
    with open(path, "r", encoding='utf-8') as f:
        text = f.read()
    return text

def write_tex(path: str, text: str):
    with open(path, "w", encoding='utf-8') as f:
        f.write(text)

def merge_tex(main_path: str, outfile):
    basepath = os.path.dirname(main_path)
    pattern = re.compile(r"\\input\{([a-zA-Z0-9_./]+)\}")
    tex = read_tex(main_path)

    new_tex = ''
    groups = [i for i in re.finditer(pattern, tex)]
    # groups = list(reversed(groups))
    for i, each_group in enumerate(groups):
        sub_tex_path = os.path.join(basepath, each_group.group(1))
        if not sub_tex_path.endswith('.tex'):
            sub_tex_path = sub_tex_path + '.tex'
        sub_tex = read_tex(sub_tex_path)
        if i == 0:
            new_tex += tex[:each_group.start()] + sub_tex + tex[each_group.end():groups[i+1].start()]
        elif i == len(groups) - 1:
            new_tex += sub_tex + tex[each_group.end():]
        else:
            new_tex += sub_tex + tex[each_group.end():groups[i+1].start()]
    if len(groups) == 0:
        new_tex = tex
    
    if isinstance(outfile, str):
        write_tex(outfile, new_tex)
    else:
        outfile.write(new_tex)

def main():
    parser = argparse.ArgumentParser(description='Diff parameters.')
    parser.add_argument('--old', type=str, required=True, help='old tex')
    parser.add_argument('--new', type=str, required=True, help='new tex')
    parser.add_argument('--out', default='diff.tex', type=str, required=False, help='output path')
    args = parser.parse_args()
    print('args:\n' + args.__repr__())

    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as old_file:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as new_file:
            merge_tex(args.old, old_file)
            merge_tex(args.new, new_file)
            old_file.flush()
            new_file.flush()

    with open(args.out, 'w') as output_f:
        cmd = f"latexdiff {old_file.name} {new_file.name}"
        print(cmd)
        p = subprocess.Popen(cmd,
                            stdout=output_f,
                            stderr=sys.stdout)
        p.wait()

if __name__ == "__main__":
    main()
