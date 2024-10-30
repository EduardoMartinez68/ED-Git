from flask import Flask, render_template, request, redirect, url_for
import git
import os
import time

app = Flask(__name__)

#--------------------------------------------------------home--------------------------------
@app.route('/')
def home():
    folders=get_all_the_projects()
    return render_template('links/home.html',folders=folders)

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
    return render_template('grap.html',dataGitFolder=dataGitFolder)


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