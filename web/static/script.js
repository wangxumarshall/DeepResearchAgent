document.getElementById('task-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const task = document.getElementById('task').value;
    const resultsContainer = document.getElementById('results-container');
    const resultsContent = document.getElementById('results-content');
    const runButton = document.getElementById('run-button');

    resultsContainer.style.display = 'block';
    resultsContent.innerHTML = 'Running agent...';
    runButton.disabled = true;
    runButton.classList.add('opacity-50', 'cursor-not-allowed');

    try {
        const response = await fetch('/run_agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task: task }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        resultsContent.innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
    } catch (error) {
        resultsContent.innerHTML = `<p class="text-red-500">An error occurred: ${error.message}</p>`;
    } finally {
        runButton.disabled = false;
        runButton.classList.remove('opacity-50', 'cursor-not-allowed');
    }
});
