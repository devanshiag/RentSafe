document.addEventListener('DOMContentLoaded', () => {
    const monthlyRent = JSON.parse(document.getElementById('monthlyRent').textContent);
    const paymentMethodElement = document.getElementById('paymentMethod');
    const processingFeeDisplay = document.getElementById('processingFeeDisplay');
    const totalAmountDisplay = document.getElementById('totalAmountDisplay');
    const payButton = document.getElementById('payButton');

    paymentMethodElement.addEventListener('change', function () {
        let processingFee = 0;

        if (this.value === 'Credit/Debit Card') {
            processingFee = (monthlyRent * 0.028).toFixed(2);
        }

        const totalAmount = (parseFloat(monthlyRent) + parseFloat(processingFee)).toFixed(2);

        processingFeeDisplay.innerHTML = `<strong>Processing Fee: ₹${processingFee}</strong>`;
        totalAmountDisplay.innerHTML = `<strong>Total Amount to Pay: ₹${totalAmount}</strong>`;

        payButton.disabled = false;
    });
});
