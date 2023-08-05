def build(file, output, data_files):
    import subprocess
    subprocess.run(f"nuitka {file} -o {output} --standalone --onefile --remove-output --include-data-file {data_files}", shell=True)