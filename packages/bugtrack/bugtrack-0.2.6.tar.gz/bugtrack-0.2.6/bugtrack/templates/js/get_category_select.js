function get_category_select(category_id) {
    $.get('{% url "ajax_get_category_select" %}?category_id=' + category_id, function(data) {
        $('#div_category').html(data);
    });
}
