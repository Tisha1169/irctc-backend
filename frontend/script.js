const API = "http://127.0.0.1:8000/api";

let isLoginMode = true;
let searchParams = {};
let selectedDate = "";
let availableDates = [];

const SAMPLE_TRAINS = [
    {
        id: 1,
        name: "Rajdhani Express",
        number: "12301",
        from: "New Delhi",
        to: "Mumbai Central",
        departure: "16:55",
        arrival: "08:35",
        duration: "15h 40m",
        availableSeats: 156,
        class: "3A",
        fare: 1450,
        status: "AVAILABLE"
    },
    {
        id: 2,
        name: "Shatabdi Express",
        number: "12002",
        from: "New Delhi",
        to: "Mumbai Central",
        departure: "06:00",
        arrival: "14:25",
        duration: "8h 25m",
        availableSeats: 0,
        class: "3A",
        fare: 1650,
        status: "WAITLIST"
    },
    {
        id: 3,
        name: "Duronto Express",
        number: "12263",
        from: "New Delhi",
        to: "Mumbai Central",
        departure: "22:25",
        arrival: "12:20",
        duration: "13h 55m",
        availableSeats: 89,
        class: "3A",
        fare: 1550,
        status: "AVAILABLE"
    },
    {
        id: 4,
        name: "August Kranti Rajdhani",
        number: "12953",
        from: "New Delhi",
        to: "Mumbai Central",
        departure: "17:20",
        arrival: "09:25",
        duration: "16h 05m",
        availableSeats: 12,
        class: "3A",
        fare: 1480,
        status: "AVAILABLE"
    },
    {
        id: 5,
        name: "Mumbai Rajdhani",
        number: "12951",
        from: "New Delhi",
        to: "Mumbai Central",
        departure: "16:30",
        arrival: "08:15",
        duration: "15h 45m",
        availableSeats: 203,
        class: "3A",
        fare: 1500,
        status: "AVAILABLE"
    }
];

function showToast(message, type = "success") {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            ${type === "success" 
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>'
            }
        </svg>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add("removing");
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

function openAuthModal() {
    document.getElementById("authModal").classList.add("active");
}

function closeAuthModal() {
    document.getElementById("authModal").classList.remove("active");
}

function toggleAuthMode() {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const modalTitle = document.getElementById("modalTitle");
    const toggleText = document.getElementById("toggleText");
    const toggleBtn = document.getElementById("toggleMode");

    isLoginMode = !isLoginMode;

    if (isLoginMode) {
        loginForm.classList.remove("hidden");
        signupForm.classList.add("hidden");
        modalTitle.innerText = "Login to Your Account";
        toggleText.innerText = "Don't have an account?";
        toggleBtn.innerText = "Sign Up";
    } else {
        loginForm.classList.add("hidden");
        signupForm.classList.remove("hidden");
        modalTitle.innerText = "Create Account";
        toggleText.innerText = "Already have account?";
        toggleBtn.innerText = "Login";
    }
}

function setLoading(buttonId, textId, isLoading) {
    const btn = document.getElementById(buttonId);
    const text = document.getElementById(textId);
    
    if (isLoading) {
        btn.disabled = true;
        text.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>';
    } else {
        btn.disabled = false;
        text.innerText = buttonId === "loginBtn" ? "Login" : "Sign Up";
    }
}

async function loginUser() {
    const username = document.getElementById("loginUsername").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    if (!username || !password) {
        showToast("Please fill in all fields", "error");
        return;
    }

    setLoading("loginBtn", "loginBtnText", true);

    try {
        const res = await fetch(`${API}/login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (!res.ok) {
            showToast(data.detail || data.error || "Login failed", "error");
            setLoading("loginBtn", "loginBtnText", false);
            return;
        }

        localStorage.setItem("accessToken", data.access);
        localStorage.setItem("refreshToken", data.refresh);
        localStorage.setItem("username", username);

        showToast("Login successful!", "success");
        updateUIForLoggedInUser(username);
        closeAuthModal();

        document.getElementById("loginUsername").value = "";
        document.getElementById("loginPassword").value = "";

    } catch (err) {
        console.error("LOGIN ERROR:", err);
        showToast("Backend not reachable", "error");
    } finally {
        setLoading("loginBtn", "loginBtnText", false);
    }
}

async function registerUser() {
    const username = document.getElementById("signupUsername").value.trim();
    const email = document.getElementById("signupEmail").value.trim();
    const password = document.getElementById("signupPassword").value.trim();

    if (!username || !email || !password) {
        showToast("Please fill in all fields", "error");
        return;
    }

    setLoading("signupBtn", "signupBtnText", true);

    try {
        const res = await fetch(`${API}/register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (!res.ok) {
            showToast(data.error || data.username?.[0] || data.email?.[0] || "Registration failed", "error");
            setLoading("signupBtn", "signupBtnText", false);
            return;
        }

        showToast("Registration successful! Please login.", "success");
        
        document.getElementById("signupUsername").value = "";
        document.getElementById("signupEmail").value = "";
        document.getElementById("signupPassword").value = "";
        
        toggleAuthMode();

    } catch (err) {
        console.error("REGISTER ERROR:", err);
        showToast("Backend not reachable", "error");
    } finally {
        setLoading("signupBtn", "signupBtnText", false);
    }
}

function updateUIForLoggedInUser(username) {
    document.getElementById("loginText").classList.add("hidden");
    document.getElementById("userInfo").classList.remove("hidden");
    document.getElementById("usernameDisplay").innerText = username;
    
    const authButton = document.getElementById("authButton");
    authButton.onclick = toggleUserDropdown;
}

function updateUIForLoggedOutUser() {
    document.getElementById("loginText").classList.remove("hidden");
    document.getElementById("userInfo").classList.add("hidden");
    document.getElementById("userDropdown").classList.add("hidden");
    
    const authButton = document.getElementById("authButton");
    authButton.onclick = handleAuthButtonClick;
}

function handleAuthButtonClick() {
    const token = localStorage.getItem("accessToken");
    if (token) {
        toggleUserDropdown();
    } else {
        openAuthModal();
    }
}

function toggleUserDropdown() {
    const dropdown = document.getElementById("userDropdown");
    dropdown.classList.toggle("hidden");
}

function logoutUser() {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("username");
    
    updateUIForLoggedOutUser();
    showToast("Logged out successfully", "success");
    showSearchPage();
}

function checkAuthStatus() {
    const token = localStorage.getItem("accessToken");
    const username = localStorage.getItem("username");
    
    if (token && username) {
        updateUIForLoggedInUser(username);
    }
}

function searchTrains() {
    const fromStation = document.getElementById("fromStation").value.trim();
    const toStation = document.getElementById("toStation").value.trim();
    const journeyDate = document.getElementById("journeyDate").value;
    const travelClass = document.getElementById("travelClass").value;
    const passengerCount = document.getElementById("passengerCount").value;

    console.log("SEARCH INITIATED", { fromStation, toStation, journeyDate, travelClass, passengerCount });

    if (!fromStation || !toStation) {
        showToast("Please enter both source and destination", "error");
        return;
    }

    if (!journeyDate) {
        showToast("Please select journey date", "error");
        return;
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selectedDateObj = new Date(journeyDate);

    if (selectedDateObj < today) {
        showToast("Please select a future date", "error");
        return;
    }

    searchParams = {
        from: fromStation,
        to: toStation,
        date: journeyDate,
        class: travelClass,
        passengers: parseInt(passengerCount)
    };

    selectedDate = journeyDate;
    generateDateScrollBar(journeyDate);
    showResultsPage();
    displayTrains();
}

function generateDateScrollBar(baseDate) {
    const dateBar = document.getElementById("dateScrollBar");
    dateBar.innerHTML = "";
    availableDates = [];

    const base = new Date(baseDate);
    
    for (let i = -3; i <= 3; i++) {
        const date = new Date(base);
        date.setDate(date.getDate() + i);
        
        const dateStr = date.toISOString().split('T')[0];
        availableDates.push(dateStr);
        
        const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
        const dayNum = date.getDate();
        const monthName = date.toLocaleDateString('en-US', { month: 'short' });
        
        const dateItem = document.createElement("div");
        dateItem.className = `date-item bg-white rounded-lg p-4 shadow-md text-center ${dateStr === selectedDate ? 'active' : ''}`;
        dateItem.setAttribute("data-date", dateStr);
        dateItem.innerHTML = `
            <div class="text-xs font-medium ${dateStr === selectedDate ? 'text-white' : 'text-gray-500'}">${dayName}</div>
            <div class="text-2xl font-bold ${dateStr === selectedDate ? 'text-white' : 'text-gray-800'}">${dayNum}</div>
            <div class="text-xs ${dateStr === selectedDate ? 'text-white' : 'text-gray-600'}">${monthName}</div>
        `;
        
        dateItem.onclick = () => selectDate(dateStr);
        dateBar.appendChild(dateItem);
    }
}

function selectDate(dateStr) {
    console.log("DATE SELECTED:", dateStr);
    selectedDate = dateStr;
    searchParams.date = dateStr;
    
    document.querySelectorAll('.date-item').forEach(item => {
        if (item.getAttribute('data-date') === dateStr) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    updateDateDisplay();
    displayTrains();
}

function scrollDates(direction) {
    const container = document.querySelector('.date-scroll-container');
    const scrollAmount = 300;
    
    if (direction === 'left') {
        container.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    } else {
        container.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
}

function showResultsPage() {
    document.getElementById("searchPage").classList.add("hidden");
    document.getElementById("resultsPage").classList.remove("hidden");
    
    updateSearchSummary();
}

function showSearchPage() {
    document.getElementById("searchPage").classList.remove("hidden");
    document.getElementById("resultsPage").classList.add("hidden");
}

function updateSearchSummary() {
    document.getElementById("routeDisplay").innerText = `${searchParams.from} → ${searchParams.to}`;
    updateDateDisplay();
    document.getElementById("passengersDisplay").innerText = `${searchParams.passengers} Passenger${searchParams.passengers > 1 ? 's' : ''}, ${searchParams.class}`;
}

function updateDateDisplay() {
    const dateObj = new Date(selectedDate);
    const formatted = dateObj.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
    document.getElementById("dateDisplay").innerText = formatted;
}

function displayTrains() {
    const trainsList = document.getElementById("trainsList");
    const loadingSpinner = document.getElementById("loadingSpinner");
    const noTrainsMessage = document.getElementById("noTrainsMessage");
    
    loadingSpinner.classList.remove("hidden");
    trainsList.innerHTML = "";
    noTrainsMessage.classList.add("hidden");
    
    setTimeout(() => {
        loadingSpinner.classList.add("hidden");
        
        const trains = SAMPLE_TRAINS.filter(train => {
            return train.from.toLowerCase().includes(searchParams.from.toLowerCase()) &&
                   train.to.toLowerCase().includes(searchParams.to.toLowerCase());
        });
        
        if (trains.length === 0) {
            noTrainsMessage.classList.remove("hidden");
            return;
        }
        
        trains.forEach(train => {
            const trainCard = createTrainCard(train);
            trainsList.appendChild(trainCard);
        });
    }, 800);
}

function createTrainCard(train) {
    const card = document.createElement("div");
    card.className = "train-card bg-white rounded-xl shadow-md p-6 border border-gray-200";
    
    const statusClass = train.status === "AVAILABLE" ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700";
    const seatsText = train.availableSeats > 0 ? `${train.availableSeats} seats available` : "Waitlist";
    
    card.innerHTML = `
        <div class="flex items-center justify-between mb-4">
            <div>
                <h3 class="text-xl font-bold text-gray-800">${train.name}</h3>
                <p class="text-sm text-gray-500">#${train.number}</p>
            </div>
            <div class="${statusClass} px-4 py-2 rounded-lg font-semibold text-sm">
                ${train.status}
            </div>
        </div>
        
        <div class="grid grid-cols-3 gap-6 mb-6">
            <div class="text-center">
                <p class="text-2xl font-bold text-gray-800">${train.departure}</p>
                <p class="text-sm text-gray-600">${train.from}</p>
            </div>
            <div class="text-center flex flex-col justify-center">
                <p class="text-sm text-gray-500 mb-1">${train.duration}</p>
                <div class="flex items-center justify-center">
                    <div class="h-px bg-gray-300 flex-1"></div>
                    <svg class="w-4 h-4 text-gray-400 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                    <div class="h-px bg-gray-300 flex-1"></div>
                </div>
            </div>
            <div class="text-center">
                <p class="text-2xl font-bold text-gray-800">${train.arrival}</p>
                <p class="text-sm text-gray-600">${train.to}</p>
            </div>
        </div>
        
        <div class="flex items-center justify-between">
            <div>
                <p class="text-sm text-gray-600">${seatsText}</p>
                <p class="text-2xl font-bold text-blue-600">₹${train.fare}</p>
            </div>
            <button 
                onclick="initiateBooking(${train.id}, '${train.name}')" 
                class="bg-gradient-to-r from-orange-500 to-orange-600 text-white px-8 py-3 rounded-lg font-bold hover:from-orange-600 hover:to-orange-700 transition-all shadow-md hover:shadow-lg"
            >
                Book Now
            </button>
        </div>
    `;
    
    return card;
}

function initiateBooking(trainId, trainName) {
    console.log("BOOKING INITIATED", { trainId, trainName, date: selectedDate, passengers: searchParams.passengers });
    
    const token = localStorage.getItem("accessToken");
    
    if (!token) {
        showToast("Please login to book tickets", "error");
        openAuthModal();
        return;
    }
    
    bookTicket(trainId, trainName);
}

async function bookTicket(trainId, trainName) {
    const token = localStorage.getItem("accessToken");
    
    const bookingData = {
        train_id: trainId,
        travel_date: selectedDate,
        seats: searchParams.passengers
    };
    
    console.log("CALLING BACKEND API", bookingData);
    
    try {
        const res = await fetch(`${API}/book/`, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(bookingData)
        });

        const data = await res.json();
        
        console.log("BOOKING RESPONSE:", data);

        if (!res.ok) {
            if (res.status === 401) {
                showToast("Session expired. Please login again", "error");
                logoutUser();
                return;
            }
            showToast(data.error || data.detail || "Booking failed", "error");
            return;
        }

        showToast(data.message || `Ticket booked successfully for ${trainName}!`, "success");
        
        setTimeout(() => {
            showSearchPage();
        }, 2000);

    } catch (err) {
        console.error("BOOKING ERROR:", err);
        showToast("Backend not reachable", "error");
    }
}

document.addEventListener("click", function(event) {
    const dropdown = document.getElementById("userDropdown");
    const authButton = document.getElementById("authButton");
    
    if (!dropdown.contains(event.target) && !authButton.contains(event.target)) {
        dropdown.classList.add("hidden");
    }
});

function setMinDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById("journeyDate").setAttribute('min', today);
}

window.addEventListener("DOMContentLoaded", () => {
    checkAuthStatus();
    setMinDate();
    console.log("IRCTC Frontend Loaded Successfully");
});