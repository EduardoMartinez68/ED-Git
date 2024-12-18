from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import git
from git import Repo
import os
import time
import subprocess
from database import *

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave_predeterminada_segura')

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

        #we will see if exist the folder, if exist we will save the information of the folder
        if os.path.isdir(element_path):
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
        else:
            delete_folder_in_database(element_path)
            
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

#--------------------------------------------------------FORM HOME--------------------------------
#create new project--------------------------------
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
        flash(f"The folder '{pathFolder}' already exists.", 'error')
        return redirect(url_for('home'))

#clone project--------------------------------
@app.route('/clone_project',methods=['POST'])
def clone_project():
    repo_url = request.form.get('linkProject')

    #get the name folder and the path where we store the product
    folderName = request.form.get('folder_name')
    pathFolderForm=request.form.get('path')

    #get the new path complete of the user 
    clone_dir = os.path.join(pathFolderForm, folderName)

    # Check if the directory already exists and is not empty
    if os.path.exists(clone_dir) and os.listdir(clone_dir):
        flash(f'Error: The directory {clone_dir} already exists and is not empty.', 'error')
        return redirect(url_for('home'))
    else:
        try:
            # Clone el repository
            git.Repo.clone_from(repo_url, clone_dir)
            save_new_project_in_the_database(clone_dir)

            flash(f"The repository was clone with success", 'success')
            return redirect(url_for('open_project_path', folder_path=clone_dir))
        except Exception as e:
            print(f'An error occurred while cloning the repository: {e}')

            flash(f"An error occurred while cloning the repository", 'error')
            return redirect(url_for('home'))

#import project--------------------------------
@app.route('/import_project',methods=['POST'])
def import_project():
    path = request.form.get('path')

    #we will see if exist a Git project in this path 
    if os.path.exists(path):
        if save_new_project_in_the_database(path): #we will see if can save the path in the database
            return redirect(url_for('open_project_path', folder_path=path))

    return redirect(url_for('home')) #$if exist a error, return the home










#------------------------------------------------------create new branch and commit------------------------------
@app.route('/create_new_branch',methods=['POST'])
def create_new_branch():
    folderPath = request.form.get('folderPath') 
    branchName = request.form.get('branchName') 
    branchName = branchName.replace(' ', '_') #this is for that when, we will create the new branch, the space in empty not can create a error in Git 

    #we will see if can create the new branch, else redirect to the user to home 
    if create_new_branch_in_my_project(folderPath,branchName):
        flash(f"The branch '{branchName}' has been created and now you are in it.",'success')
        return redirect(url_for('open_project_path', folder_path=folderPath))
    else:
        flash(f"The branch '{branchName}' not was create.",'error')
        return redirect(url_for('/home'))


def create_new_branch_in_my_project(repo_path, branch_name):
    try:
        # open the repository
        repo = git.Repo(repo_path)

        # we will see if the branch exist
        branch_exists = any(branch.name == branch_name for branch in repo.branches)
        if branch_exists:
            print(f"La branch '{branch_name}' exist.")
            return False

        # create a new branch and that it is the branch current
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()  # change to the new branch
        return True

    except git.exc.InvalidGitRepositoryError:
        print("Error: The path provided is not a valid Git repository.")
        return False
    except Exception as e:
        print(f"Error in create_new_branch_in_my_project: {e}")
        return False


@app.route('/create_a_new_commit',methods=['POST'])
def create_a_new_commit():
    pathProject = request.form.get('pathProject') 
    branchName = request.form.get('branchName') 
    commitMessage=request.form.get('commit') 

    #we will see if can create the commit
    if create_commit(pathProject,branchName,commitMessage):
        flash(f'The commit was create with success', 'success')
        return redirect(url_for('open_project_path', folder_path=pathProject))
    
    flash(f'The commit not was create', 'error')
    return redirect(url_for('open_project_path', folder_path=pathProject))


def create_commit(repoPath, branchName, commitMessage):
    print(repoPath)
    print(branchName)
    print(commitMessage)

    try:
        # Open the repository
        repo = git.Repo(repoPath)

        # Check if the branch exists
        if branchName not in repo.branches:
            # Create the branch if it doesn't exist
            repo.git.checkout('-b', branchName)
        else:
            # Switch to the existing branch
            repo.git.checkout(branchName)

        # Add all the changes to the staging area
        repo.git.add(A=True)

        # Create a new commit
        repo.index.commit(commitMessage)
        return True

    except Exception as e:
        print(f"An error occurred while creating the commit create_commit: {e}")
        return False




@app.route('/change_branch_of_my_project',methods=['POST'])
def change_branch_of_my_project():
    folderPath = request.form.get('folderPath') 
    branchName=request.form.get('branchName')
    branchName=branchName.lower() #this is for convert the text of uppercase to lowercase

    #we will see if can create the new branch, else redirect to the user to home 
    if change_branch(folderPath,branchName):
        flash(f"You moved to the branch '{branchName}' with success.",'success')
        return redirect(url_for('open_project_path', folder_path=folderPath))
    else:
        flash(f"You can't move to the branch. Try again",'error')
        return redirect(url_for('open_project_path', folder_path=folderPath))


def change_branch(folderPath,branchName):
    try:
        # open the repository
        repo = git.Repo(folderPath)

        # Check if the branch already exists in the repository
        if branchName in repo.branches:
            # change to the branch exis
            repo.git.checkout(branchName)
        else:
            # Crea una nueva rama y cambia a ella
            repo.git.checkout('-b', branchName)

        return True
    except Exception as e:
        print(f"An error occurred while switching branches change_branch: {e}")
        return False 
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

    #we will see if can read the git project
    if dataGitFolder==None:
        flash('The project could not be imported. Check the path or if it already exists.', 'error')
        return redirect(url_for('home')) #if the git project not was can be read, show a error
    else:
        currentBranch=get_branch_current_of_the_project(folder_path)
        update_modification_date(folder_path)
        return render_template('links/tree.html',dataGitFolder=dataGitFolder,currentBranch=currentBranch,folder_path=folder_path)

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
        return None

def get_branch_current_of_the_project(repoPath):
    repo = Repo(repoPath)

    # Check if the repository is not in a 'detached' state
    if not repo.bare:
        currentBranch = repo.active_branch
        return currentBranch
    else:
        print("The repository is in a 'detached' state or is not a valid repository.")
        return None



#-----------------------------------------------------CONSOLE--------------------------
'''
    this is for when the user would like know that files was edit in his project in Git
'''
@app.route('/get_changes_of_my_project', methods=['POST'])
def get_changes_of_my_project():
    # Get the data from the client
    data = request.get_json()
    folder_path = data.get('folderPath')

    try:
        # Check if the path exists
        if not os.path.exists(folder_path):
            return jsonify({"answer": "The specified path does not exist."})

        # Check if there is a Git project in the path
        repo = git.Repo(folder_path)
        if repo.bare:
            return jsonify({"answer": "The specified path is not a valid Git repository."})

        # Get changes in the index (staged files)
        changed_files = [item.a_path for item in repo.index.diff(None)]
        
        # Get committed changes (files in the last commit)
        try:
            committed_changes = []
            if repo.head.is_valid():  # Ensure the HEAD is valid
                committed_changes = [item.a_path for item in repo.head.commit.diff('HEAD~1')]
        except Exception as e:
            committed_changes = []  # No previous changes

        # Get untracked files
        untracked_files = repo.untracked_files

        # Combine all changes
        all_changes = changed_files + committed_changes + untracked_files
        
        if all_changes:
            answer = f"" + '\n'.join(all_changes)
        else:
            answer = "No changes have been detected."

        return jsonify({"answer": answer})

    except git.GitCommandError as e:
        return jsonify({"answer": f"A Git error occurred: {str(e)}"})
    except Exception as e:
        return jsonify({"answer": f"An error occurred: {str(e)}"})
    
def get_changes_of_my_project2():
    #we will get the data of the client
    data = request.get_json()
    folder_path = data.get('folderPath')

    try:
        #we will see if exist the path
        if not os.path.exists(folder_path):
            return jsonify({"answer": "The specified path does not exist."})

        #we will see if exist a project Git in the path
        repo = git.Repo(folder_path)
        if repo.bare:
            return jsonify({"answer": "The specified path is not a valid Git repository."})

        #get the change of the files
        changed_files = [item.a_path for item in repo.index.diff(None)]
        
        #Handle case where there are not enough confirmations
        try:
            committed_changes = repo.head.commit.diff('HEAD~1')
        except Exception as e:
            committed_changes = []  #There are no previous changes

        all_changes = changed_files + [item.a_path for item in committed_changes]

        if all_changes:
            answer = f"Modified files: {', '.join(all_changes)}"
        else:
            answer = "No changes have been detected."

        return jsonify({"answer": answer})

    except git.GitCommandError as e:
        return jsonify({"answer": f"A Git error occurred: {str(e)}"})
    except Exception as e:
        return jsonify({"answer": f"An error occurred:{str(e)}"})









#-------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)


#this is for that we get the path of the folder of the git project
@app.route('/submit', methods=['POST'])
def submit():
    folder_path = request.form.get('folder_path')
    print("Dirección de la carpeta seleccionada:", folder_path)
    return "La dirección de la carpeta ha sido recibida. Revisa la consola."

if __name__ == "__main__":
    app.run(debug=True)