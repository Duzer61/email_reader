$(document).ready(function() {
    let messagesContainer = $('#messages-container');
    let progressContainer = $('#progress-container');
    let progress = $('progress');
    const socket = new WebSocket(
        'ws://'
        + window.location.host
        + '/ws/'
    );

    $('#email-select').change(function() {
        messagesContainer.html('<p>Готов к загрузке...</p>');
    });

    $('#button').click(function() {
        $(this).prop('disabled', true);
        const selectedEmail = $('#email-select').val();
        socket.send(JSON.stringify({ 'email_acc': selectedEmail }));
        $('table').find('tr:gt(0)').remove();
    });

    socket.addEventListener('message', function(event) {
        let data = JSON.parse(event.data);
        // Вывод информационных сообщений
        if (data.result) {
            let message = data.result;
            if (message !== undefined) {
                messagesContainer.html(`<p>${message}</p>`);
            }
        }
        // Вывод строк в таблицу
        if (data.table_row) {
            let tableData = data.table_row;
            let table = $('table');
            let newRow = $('<tr>').appendTo(table);

            newRow.append(
                $('<td>').text(tableData.subject),
                $('<td>').text(tableData.sent),
                $('<td>').text(tableData.received),
                $('<td>').text(tableData.text),
                $('<td>').html(tableData.attachments),
                $('<td>').text(tableData.message_id)
            );
        }
        // Вывод прогресс-бара
        if (data.progress) {
            let total = data.total;
            progressContainer.css('display', 'block');
            progress.val(data.progress);
            progress.attr('max', total);
            progress.css('--progress-after-content', `'Осталось: ${progress.attr('max') - progress.val()}'`);
            if (progress.val() / total > 0.55) {
                progress.css('--progress-after-color', 'white');
            } else {
                progress.css('--progress-after-color', 'black');
            }
        }
        // Сигнал окончания загрузки
        if (data.flag) {
            progress.css('--progress-after-content', `'Загрузка завершена'`);
            progressContainer.delay(2500).fadeOut(200);
            $('#button').prop('disabled', false);
        }
    });

    socket.addEventListener('close', function(event) {
        console.log('WebSocket connection closed:', event);
    });
});