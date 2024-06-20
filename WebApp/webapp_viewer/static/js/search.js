document.addEventListener('DOMContentLoaded', function(){
    var form = document.getElementById('searchForm');
    if(form){
        form.addEventListener('submit', function(e){
        e.preventDefault();
        const searchTerm = document.getElementById('searchInput').value.trim();
        
        fetch(`/api/search_organizations/?query=${encodeURIComponent(searchTerm)}`)
            .then(response => response.json())
            .then(data => {
                if(data && data.id){
                    window.location.href = `/organizations/${data.id}`;
                } else {
                    alert('Organization not found.');
                }
            })

            .catch(error => {
                console.error('Error during search', error);
                alert('error. try again');
            });
        });
    }
});
