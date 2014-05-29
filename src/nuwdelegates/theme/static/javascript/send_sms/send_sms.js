// Set character limit on textarea.
function characterLimit(field, charcount, limit) {
    if (field.value.length > limit) {
        field.value = field.value.substring(0, limit);
    } else {
        charcount.value = limit - field.value.length;
    }
}
