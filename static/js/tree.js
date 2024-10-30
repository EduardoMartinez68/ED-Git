document.addEventListener("DOMContentLoaded", () => {
    const dataGitFolder = {{ dataGitFolder | tojson
}};

const branches = dataGitFolder.branches.map(branch => ({
    name: branch.toUpperCase(),
    color: getBranchColor(branch)
}));

const commits = [];
for (const branchName in dataGitFolder.commits) {
    dataGitFolder.commits[branchName].forEach(commit => {
        commits.push({
            id: commit.hash,
            branch: branchName.toUpperCase(),
            message: commit.message,
            author: commit.author,
            date: commit.date
        });
    });
}

renderDiagram(branches, commits);
});

function getBranchColor(branchName) {
    const colors = {
        'MAIN': '#FF6B6B',
        'MASTER': '#FF6B6B',
        'HOT': '#4C6EF5',
        'RELEASE': '#FF79C6',
        'DEVELOP': '#FFD166',
        'FEATURE': '#06D6A0'
    };
    return colors[branchName.toUpperCase()] || '#AAAAAA';
}

function renderDiagram(branches, commits) {
const diagramContainer = document.getElementById('diagram');
const tooltip = document.getElementById('tooltip');

branches.forEach(branch => {
const branchContainer = document.createElement('div');
branchContainer.classList.add('branch');
branchContainer.dataset.branch = branch.name;

const branchTitle = document.createElement('div');
branchTitle.classList.add('branch-title');
branchTitle.style.backgroundColor = branch.color;
branchTitle.textContent = branch.name;
branchContainer.appendChild(branchTitle);

const branchCommits = commits.filter(commit => commit.branch === branch.name);

// Almacenar los elementos de commit para usarlos después en la conexión
const commitElements = [];

branchCommits.forEach(commit => {
    const commitElement = document.createElement('div');
    commitElement.classList.add('commit');
    commitElement.id = commit.id;
    commitElement.dataset.message = commit.message;

    // Event listeners para mostrar el tooltip
    commitElement.addEventListener('mouseenter', (e) => {
        tooltip.textContent = commit.message;
        tooltip.style.display = 'block';
        commitElement.style.cursor = 'pointer'; // Cambiar el cursor a pointer
    });

    commitElement.addEventListener('mousemove', (e) => {
        tooltip.style.left = e.pageX + 10 + 'px';
        tooltip.style.top = e.pageY + 10 + 'px';
    });

    commitElement.addEventListener('mouseleave', () => {
        tooltip.style.display = 'none';
    });

    branchContainer.appendChild(commitElement);
    commitElements.push(commitElement); // Agregar el commit a la lista
});

diagramContainer.appendChild(branchContainer);

// Conectar los commits de esta rama después de haberlos agregado al DOM
for (let i = 0; i < commitElements.length - 1; i++) {
    connectCommits(commitElements[i], commitElements[i + 1]);
}
});
}
function connectCommits(commitA, commitB) {
    const svgContainer = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svgContainer.setAttribute("class", "connection");
    svgContainer.style.position = "absolute";
    svgContainer.style.top = "0";
    svgContainer.style.left = "0";
    svgContainer.style.width = "100%";
    svgContainer.style.height = "100%";
    document.body.appendChild(svgContainer);

    const rectA = commitA.getBoundingClientRect();
    const rectB = commitB.getBoundingClientRect();

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute("x1", rectA.x + rectA.width / 2);
    line.setAttribute("y1", rectA.y + rectA.height / 2);
    line.setAttribute("x2", rectB.x + rectB.width / 2);
    line.setAttribute("y2", rectB.y + rectB.height / 2);
    line.setAttribute("stroke", "#ccc");
    line.setAttribute("stroke-width", "2");

    svgContainer.appendChild(line);
}