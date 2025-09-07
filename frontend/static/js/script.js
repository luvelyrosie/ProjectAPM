// Start Order
async function startOrder(orderId) {
    try {
        const response = await fetch(`/orders/${orderId}/start`, {
            method: 'POST'
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

// Complete Order
async function completeOrder(orderId) {
    try {
        const response = await fetch(`/orders/${orderId}/complete`, {
            method: 'POST'
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

// Reject Order
async function rejectOrder(orderId) {
    const reason = prompt("Введите причину отклонения заказа:");
    if (!reason) return alert("Причина отклонения обязательна!");

    try {
        const response = await fetch(`/orders/${orderId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: reason })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}


// Start Task
async function takeTask(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/start`, {
            method: 'POST'
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

// Complete Task
async function completeTask(taskId) {
    try {
        const response = await fetch(`/tasks/${taskId}/complete`, {
            method: 'POST'
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}

// Reject Task
async function rejectTask(taskId) {
    const reason = prompt("Введите причину отклонения задания:");
    if (!reason) return alert("Причина отклонения обязательна!");

    try {
        const response = await fetch(`/tasks/${taskId}/reject`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: reason })
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || data.message);
        alert(data.message);
        location.reload();
    } catch (err) {
        alert(`Ошибка: ${err.message}`);
    }
}
