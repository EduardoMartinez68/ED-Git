// Funciones de ejemplo para los botones
function createNewProject() {
    alert("Crear un nuevo proyecto");
}

function loadProject() {
    // Crear un input tipo "file" que acepte solo directorios
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true; // Solo funciona en Chrome

    input.onchange = async (e) => {
        const folderPath = e.target.files[0].webkitRelativePath.split('/')[0];
        document.getElementById('folder_path').value = folderPath;

        // Enviar la dirección de la carpeta al servidor
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                folder_path: folderPath,
            }),
        });

        // Manejar la respuesta
        if (response.ok) {
            const text = await response.text();
            console.log(text); // Mostrar la respuesta en la consola
        } else {
            console.error('Error al enviar la dirección de la carpeta.');
        }
    };

    input.click();
}

function openProject(projectName) {
    alert("Abriendo " + projectName);
}


function restartAllTheForms(form){
    //restart the form that close the user
    toggleForm(form)

    //get the path of the ED folder
    const pathUser=document.getElementById('pathFolderED').value;

    //we will get all the path input of the form and update
    document.getElementById('pathOpen').value='';
    document.getElementById('pathNew').value=pathUser;
    document.getElementById('pathClone').value=pathUser;
}