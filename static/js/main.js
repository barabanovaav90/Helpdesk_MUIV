/**
 * JavaScript-утилиты Helpdesk-системы.
 *
 * Содержит логику для интерактивных элементов:
 * - FAQ-аккордеон
 * - Автоскрытие уведомлений
 * - Подтверждение действий
 */

document.addEventListener('DOMContentLoaded', function () {

    // ── FAQ Аккордеон ──────────────────────────────────────────
    document.querySelectorAll('.faq-question').forEach(function (question) {
        question.addEventListener('click', function () {
            const item = this.closest('.faq-item');
            const wasOpen = item.classList.contains('open');

            // Закрыть все
            document.querySelectorAll('.faq-item.open').forEach(function (openItem) {
                openItem.classList.remove('open');
            });

            // Открыть текущий (если был закрыт)
            if (!wasOpen) {
                item.classList.add('open');
            }
        });
    });

    // ── Автоскрытие уведомлений ────────────────────────────────
    document.querySelectorAll('.alert-helpdesk').forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // ── Подтверждение опасных действий ─────────────────────────
    document.querySelectorAll('[data-confirm]').forEach(function (element) {
        element.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Вы уверены?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // ── Показ имени файла при выборе ───────────────────────────
    document.querySelectorAll('input[type="file"]').forEach(function (input) {
        input.addEventListener('change', function () {
            const label = this.nextElementSibling;
            if (label && label.classList.contains('custom-file-label')) {
                const files = Array.from(this.files).map(f => f.name);
                label.textContent = files.join(', ') || 'Выберите файл';
            }
        });
    });
});
