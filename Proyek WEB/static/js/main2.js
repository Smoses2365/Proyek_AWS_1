
function rentCar(stockId) {
    let stockElement = document.getElementById(stockId);
    let stock = parseInt(stockElement.textContent);
    if (stock > 0) {
        stock--;
        stockElement.textContent = stock;
        alert("Permohonan berhasil!");
    } else {
        alert("Maaf, mobil ini sudah habis disewa.");
    }
}

function filterCars() {
    let selectedBrand = document.getElementById("brand-filter").value;
    let selectedPrice = document.getElementById("price-filter").value;
    let selectedCapacity = document.getElementById("capacity-filter").value;
    let cars = document.querySelectorAll(".card");

    cars.forEach(car => {
        let carBrand = car.getAttribute("data-brand");
        let carPrice = car.getAttribute("data-price");
        let carCapacity = car.getAttribute("data-capacity");

        let brandMatch = selectedBrand === "all" || carBrand === selectedBrand;
        let priceMatch = selectedPrice === "all" || parseInt(carPrice) <= parseInt(selectedPrice);
        let capacityMatch = selectedCapacity === "all" || carCapacity === selectedCapacity;

        if (brandMatch && priceMatch && capacityMatch) {
            car.style.display = "block";
        } else {
            car.style.display = "none";
        }
    });
}
