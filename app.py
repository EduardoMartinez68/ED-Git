from flask import Flask, render_template, request, redirect, url_for
import git
import os
import time
import subprocess
from database import *

app = Flask(__name__)
folderProgram = "EDCode" 

create_database() #when the program start, we will see if exist the database, if not exist we will create

#--------------------------------------------------------home--------------------------------
@app.route('/')
def home():
    folders=get_all_the_folders_in_the_database() #get_all_the_projects()
    foldersInfo=get_the_information_of_the_folders(folders)
    userPath = get_path_user()
    return render_template('links/home.html',foldersInfo=foldersInfo,userPath=userPath)

def get_path_user():
    userPath = os.path.expanduser("~")
    return os.path.join(userPath, folderProgram)


def get_the_information_of_the_folders(folders):
    # Filter and show only folders
    folders_info = []
    for folder in folders:
        element_path = folder[1] #this is the path

        #Get dates
        creation_time = os.path.getctime(element_path)  # creation date
        modification_time = os.path.getmtime(element_path)  #Last modified date

        #Convert timestamp to readable format
        creation_time = time.ctime(creation_time)
        modification_time = folder[2]#time.ctime(modification_time)

        # Get folder name from the path
        folder_name = os.path.basename(element_path)  # Extract the folder name

        #Store information in a dictionary
        folders_info.append({
            "name": folder_name,
            "path": element_path,
            "creation_time": creation_time,
            "modification_time": modification_time
        })
        
    return folders_info

def get_all_the_projects():
    #get the path of the user
    userPath = os.path.expanduser("~")
    folderName = "EDCode" 
    pathFolder = os.path.join(userPath, folderName)

    # we going to see if exist the folder, if not exist the folder, we will to create
    if not os.path.isdir(pathFolder):
        os.makedirs(pathFolder)  # create folder

    try:
        # List all items at the specified path
        elements = os.listdir(pathFolder)

        # Filter and show only folders
        folders_info = []
        for element in elements:
            element_path = os.path.join(pathFolder, element)
            if os.path.isdir(element_path):
                #Get information about the folder
                folder_name = element
                folder_path = element_path

                #Get dates
                creation_time = os.path.getctime(element_path)  # creation date
                modification_time = os.path.getmtime(element_path)  #Last modified date

                #Convert timestamp to readable format
                creation_time = time.ctime(creation_time)
                modification_time = time.ctime(modification_time)

                #Store information in a dictionary
                folders_info.append({
                    "name": folder_name,
                    "path": folder_path,
                    "creation_time": creation_time,
                    "modification_time": modification_time
                })
            
        return folders_info

    except Exception as e:
        print(f"Error al leer la ruta: {e}")
        return []


#--------------------------------------------------------create new project--------------------------------
@app.route('/create_project',methods=['POST'])
def create_project():
    #get the name folder and the path where we store the product
    folderName = request.form.get('folder_name')
    pathFolderForm=request.form.get('path')

    #get the new path complete of the user 
    pathFolder = os.path.join(pathFolderForm, folderName)

    #we will see if exist the folder in the path. If the folder not exist, we will to create
    if not os.path.exists(pathFolder):
        os.makedirs(pathFolder)
        subprocess.run(["git", "init"], cwd=pathFolder) # create the project Git

        save_new_project_in_the_database(pathFolder)

        return redirect(url_for('open_project_path', folder_path=pathFolder))
    else:
        print(f"La carpeta '{pathFolder}' ya existe.")
        return redirect(url_for('form_create_project'))

#--------------------------------------------------------clone project--------------------------------
@app.route('/clone_project',methods=['POST'])
def clone_project():
    repo_url = request.form.get('linkProject')

    #get the name folder and the path where we store the product
    folderName = request.form.get('folder_name')
    pathFolderForm=request.form.get('path')

    #get the new path complete of the user 
    clone_dir = os.path.join(pathFolderForm, folderName)

    # Verifica si el directorio ya existe y no está vacío
    if os.path.exists(clone_dir) and os.listdir(clone_dir):
        print(f'Error: El directorio {clone_dir} ya existe y no está vacío.')
        return redirect(url_for('home'))
    else:
        try:
            # Clonar el repositorio
            git.Repo.clone_from(repo_url, clone_dir)
            print(f'Repositorio clonado en: {clone_dir}')
            save_new_project_in_the_database(clone_dir)

            return redirect(url_for('open_project_path', folder_path=clone_dir))
        except Exception as e:
            print(f'Ocurrió un error al clonar el repositorio: {e}')
            return redirect(url_for('home'))

#--------------------------------------------------------import project--------------------------------
@app.route('/import_project',methods=['POST'])
def import_project():
    path = request.form.get('path')

    #we will see if exist a Git project in this path 
    if os.path.exists(path):
        if save_new_project_in_the_database(path): #we will see if can save the path in the database
            return redirect(url_for('open_project_path', folder_path=path))

    return redirect(url_for('home')) #$if exist a error, return the home










#------------------------------------------------------create new branch------------------------------
@app.route('/create_new_branch',methods=['POST'])
def create_new_branch():
    folderPath = request.form.get('folderPath') 
    branchName = request.form.get('branchName') 
    create_new_branch_in_my_project(folderPath,branchName)
    return redirect(url_for('open_project_path', folder_path=folderPath))


def create_new_branch_in_my_project(repo_path, branch_name):
    try:
        # Abre el repositorio
        repo = git.Repo(repo_path)
        
        # Verifica si la rama ya existe
        if branch_name in repo.branches:
            print(f"La rama '{branch_name}' ya existe.")
            return False
        
        # Crea una nueva rama y la hace la rama actual
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()  # Cambia a la nueva rama
        
        print(f"La rama '{branch_name}' ha sido creada y ahora estás en ella.")
        return True

    except git.exc.InvalidGitRepositoryError:
        print("Error: La ruta proporcionada no es un repositorio Git válido.")
        return False
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")
        return False


@app.route('/create_new_commit',methods=['POST'])
def create_new_commit():
    folderPath = request.form.get('folderPath') 
    branchName = request.form.get('branchName') 
    commitMessage=request.form.get('commit') 
    create_commit(folderPath,branchName,commitMessage)
    return redirect(url_for('open_project_path', folder_path=folderPath))

def create_commit(repoPath, branchName, commitMessage):
    try:
        # Abre el repositorio
        repo = git.Repo(repoPath)

        # Cambia a la rama especificada
        repo.git.checkout(branchName)

        # Agrega todos los cambios al área de preparación (staging)
        repo.git.add(A=True)  # Agrega todos los archivos modificados

        # Crea un nuevo commit
        repo.index.commit(commitMessage)
        print(f"Commit creado en la rama '{branchName}' con el mensaje: '{commitMessage}'")

    except Exception as e:
        print(f"Ocurrió un error al crear el commit: {e}")

#-----------------------------------------------------show the folder--------------------------
@app.route('/open_project',methods=['POST'])
def open_project():
    folder_path = request.form.get('folder_path') #get the path of the folder and convert in link html
    return redirect(url_for('open_project_path', folder_path=folder_path))


'''
we will get the path folder with help of the form "open_project" for that when the user loaded the web, 
can get the data of the folder without restarting the website
'''
@app.route('/open_project/<path:folder_path>',methods=['GET']) 
def open_project_path(folder_path):
    dataGitFolder=read_git_folder_in_project(folder_path)
    update_modification_date(folder_path)
    return render_template('links/tree.html',dataGitFolder=dataGitFolder,folder_path=folder_path)


def read_git_folder_in_project(repo_path):
    try:
        repo = git.Repo(repo_path)
        
        # Get branches
        branches = [branch.name for branch in repo.branches]
        
        # Get commits with branch information
        branch_commits = {}
        for branch in repo.branches:
            branch_commits[branch.name] = []
            for commit in repo.iter_commits(branch):
                branch_commits[branch.name].append({
                    "hash": commit.hexsha,
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat()
                })

        return {"branches": branches, "commits": branch_commits}
    
    except Exception as e:
        print(f"Error accessing repository: {e}")
        return {"branches": [], "commits": {}}

#this is for that we get the path of the folder of the git project
@app.route('/submit', methods=['POST'])
def submit():
    folder_path = request.form.get('folder_path')
    print("Dirección de la carpeta seleccionada:", folder_path)
    return "La dirección de la carpeta ha sido recibida. Revisa la consola."

if __name__ == "__main__":
    app.run(debug=True)