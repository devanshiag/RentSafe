function showRequestDetails(category, description, admin_comments, createdDate, status) {
    document.getElementById('detail-title').innerText = category;
    document.getElementById('detail-description').innerText = "Description: " + description;
    document.getElementById('detail-admin_comments').innerText = "Admin Comments: " + admin_comments;
    document.getElementById('detail-created').innerText = 'Date Created: ' + createdDate;

    const statusElement = document.getElementById('detail-status');
    statusElement.innerText = 'Current Status: ' + status;

}