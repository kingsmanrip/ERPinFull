// Construction ERP JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Show active tab based on URL hash
    const hash = window.location.hash;
    if (hash) {
        const tab = document.querySelector(`[data-bs-target="${hash}"]`);
        if (tab) {
            const tabInstance = new bootstrap.Tab(tab);
            tabInstance.show();
        }
    }

    // Update URL hash when tab is changed
    const tabEls = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabEls.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', function (event) {
            window.location.hash = event.target.getAttribute('data-bs-target');
        });
    });

    // Calculate hours worked in work log form
    const entryTimeInput = document.getElementById('entry_time');
    const exitTimeInput = document.getElementById('exit_time');
    const lunchDurationInput = document.getElementById('lunch_duration');
    const hoursWorkedDisplay = document.getElementById('hours_worked_display');

    function calculateHoursWorked() {
        if (entryTimeInput && exitTimeInput && lunchDurationInput) {
            const entryTime = entryTimeInput.value;
            const exitTime = exitTimeInput.value;
            const lunchDuration = parseInt(lunchDurationInput.value) || 0;

            if (entryTime && exitTime) {
                // Convert times to minutes since midnight
                const entryMinutes = timeToMinutes(entryTime);
                const exitMinutes = timeToMinutes(exitTime);

                // Calculate total minutes worked
                let totalMinutes = exitMinutes - entryMinutes;
                
                // Apply lunch deduction (30 minutes if lunch_duration > 30)
                const lunchDeduction = lunchDuration > 30 ? 30 : 0;
                totalMinutes -= lunchDeduction;

                // Convert back to hours
                const hoursWorked = Math.max(0, totalMinutes / 60);
                
                if (hoursWorkedDisplay) {
                    hoursWorkedDisplay.textContent = hoursWorked.toFixed(2);
                }
            }
        }
    }

    function timeToMinutes(timeStr) {
        const [hours, minutes] = timeStr.split(':').map(Number);
        return hours * 60 + minutes;
    }

    // Add event listeners for time inputs
    if (entryTimeInput && exitTimeInput && lunchDurationInput) {
        entryTimeInput.addEventListener('change', calculateHoursWorked);
        exitTimeInput.addEventListener('change', calculateHoursWorked);
        lunchDurationInput.addEventListener('change', calculateHoursWorked);
        lunchDurationInput.addEventListener('input', calculateHoursWorked);
    }

    // Toggle check details in financials form
    const paymentMethodSelect = document.getElementById('paid_payment_method');
    const checkDetails = document.querySelectorAll('.check-details');
    
    if (paymentMethodSelect && checkDetails.length > 0) {
        paymentMethodSelect.addEventListener('change', function() {
            if (this.value === 'check') {
                checkDetails.forEach(el => el.style.display = 'block');
            } else {
                checkDetails.forEach(el => el.style.display = 'none');
            }
        });
        
        // Initial state
        if (paymentMethodSelect.value === 'check') {
            checkDetails.forEach(el => el.style.display = 'block');
        } else {
            checkDetails.forEach(el => el.style.display = 'none');
        }
    }

    // Initialize any charts if they exist
    initializeCharts();
});

function initializeCharts() {
    // Payment Method Chart
    const paymentMethodChartEl = document.getElementById('paymentMethodChart');
    if (paymentMethodChartEl) {
        // This is just a placeholder - in a real app, you would use a charting library
        // like Chart.js to create actual charts
        paymentMethodChartEl.innerHTML = '<div class="text-center pt-5">Payment Method Chart would be displayed here using a charting library like Chart.js</div>';
    }

    // Paid Method Chart
    const paidMethodChartEl = document.getElementById('paidMethodChart');
    if (paidMethodChartEl) {
        // This is just a placeholder - in a real app, you would use a charting library
        paidMethodChartEl.innerHTML = '<div class="text-center pt-5">Paid Accounts by Method Chart would be displayed here using a charting library like Chart.js</div>';
    }
}
