document.addEventListener('DOMContentLoaded', () => {
    const counterElement = document.getElementById('organizationCounter');
    
    fetch('/api/organizations/count')
    .then(response => response.json())
    .then(data =>{

        animateCounter(counterElement, data.count);
    })

    .catch(error => {
        console.error('Error fetching organization count:', error);
    });
});

function animateCounter(element, target){
    const speed = 200;
    let count =0;

    const updateCount = () => {
        const increment = target/speed;

        if(count < target){
            count += increment;
            element.textContent = Math.ceil(count);
            setTimeout(updateCount, 1);
        }else{
            element.textContent = target;
        }
    };
    updateCount();
}