import subprocess
from os import listdir, mkdir
import fileinput

PROJECT_DIRECTORY = '/home/tyson/PycharmProjects'


def manifest_template(project_directory: str):
    app_path = f"{project_directory}/.buildozer/android/platform/build-armeabi-v7a/dists"
    app_name = listdir(app_path)[0]
    template_directory = f"{app_path}/{app_name}/templates"
    if "AndroidManifest.tmpl.xml" in listdir(template_directory):
        return f"{template_directory}/AndroidManifest.tmpl.xml"
    return None


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
    file_paths_dir = manifest.replace("templates/AndroidManifest.tmpl.xml", "src/main/res")
    if not is_xml_dir(file_paths_dir):
        mkdir(f"{file_paths_dir}/xml")
    if file_paths_xml_exists(f"{file_paths_dir}/xml"):
        print("file_paths.xml already exists")
        deploy_project()
        return
    file_paths_xml = f"{file_paths_dir}/xml/file_paths.xml"
    add_file_paths_xml(file_paths_xml)
    #deploy_project()


if __name__ == '__main__':
    main()
