// Forçar redimensionamento dinâmico
window.addEventListener('resize', function() {
    const tables = document.querySelectorAll('.dash-spreadsheet-inner');
    tables.forEach(table => {
        table.style.minWidth = '100%';
        table.style.width = 'auto';
    });
});