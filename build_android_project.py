import subprocess
from os import listdir, mkdir
import fileinput

PROJECT_DIRECTORY = '/home/tyson/PycharmProjects'


def manifest_template(project_directory: str):
    app_path = f"{project_directory}/.buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/sdl2/build"
    template_directory = f"{app_path}/templates"
    if "AndroidManifest.tmpl.xml" in listdir(template_directory):
        return f"{template_directory}/AndroidManifest.tmpl.xml"
    return None


def xml_template(project_directory: str):
    return f"{project_directory}/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/bootstrap_builds/sdl2/src/main/res"


def check_for_existing_file_provider(file: str):
    with open(file) as f:
        return "<provider" in f.read()


def is_built(directory: str):
    return ".buildozer" in listdir(directory)


def is_xml_dir(directory: str):
    return "xml" in listdir(directory)


def file_paths_xml_exists(directory: str):
    return "file_paths.xml" in listdir(directory)


def insert_provider(file: str, file_provider: str):
    file_provider_line = None
    with open(file_provider) as fp:
        with fileinput.FileInput(file, inplace=True) as f:
            for ind, line in enumerate(f):
                if "</receiver>" in line:
                    file_provider_line = ind + 1
                if ind == file_provider_line:
                    line = line.replace(line, f"{line}\n{fp.read()}")
                print(line, end='')


def add_file_paths_xml(file_name: str):
    with open(file_name, "w") as f:
        with open("file_paths.xml", "r") as fp:
            text = fp.read()
            edited_text = text.replace("directory_name", "app/database/")
            edited_text2 = edited_text.replace("directory", "database")
            f.write(edited_text2)


def build_project():
    subprocess.Popen(['buildozer', '-v', 'android', 'debug'])


def deploy_project():
    subprocess.Popen(['buildozer -v android debug && buildozer android deploy run logcat -c > log.txt'],
                     shell=True)


def main():
    project = f"{PROJECT_DIRECTORY}/Seagrave"
    if not is_built(project):
        print("Project hasn't been compiled yet")
        #build_project()
        return
    manifest = manifest_template(project)
    if not manifest:
        print("Android Manifest template hasn't been generated")
        return
    provider_exists = check_for_existing_file_provider(manifest)
    if not provider_exists:
        file_provider = 'file_provider.xml'
        insert_provider(manifest, file_provider)

    #deploy_project()


if __name__ == '__main__':
    main()
