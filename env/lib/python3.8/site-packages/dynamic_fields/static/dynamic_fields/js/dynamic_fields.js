(function($) {
    $.fn.dynamic_field = function (opts) {
        opts = opts || {};

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = $.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        function getCsrfToken() {
            var csrftoken = getCookie('csrftoken');
            if (!csrftoken) {
                csrftoken = $('[name=csrfmiddlewaretoken]').val();
            }
            return csrftoken;
        }
        function cast_python_bool_to_js(b) {
            return b === 'True';
        }
        function fetch_choices(initial) {
            if (loading) {
                return;
            }

            if (depends_element.val()) {
                loading = true;
                $.ajax({
                    url: '/dynamic_fields/choices/',
                    method: 'POST',
                    data: {
                        'model': model,
                        'field': depends,
                        'value': depends_element.val(),
                        'call': callback
                    },
                    beforeSend: function(xhr, settings) {
                        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
                        }
                    },
                    success: function(data) {
                        update_choices(data);

                        if (initial_value) {
                            if (self.find('option[value='+initial_value+']').length > 0) {
                                self.val(initial_value);
                                self.trigger('change');
                            }
                        }
                        loading = false;
                    },
                    error: function (xhr) {
                        console.log(xhr);
                        loading = false;
                    }
                });
            }
            else {
                if (no_value_disable) {
                    self.prop('disabled', true);
                }
            }
        }
        function update_choices(choices) {
            self.empty();
            if (include_empty_choice) {
                self.append('<option value="">'+empty_choice_label+'</option>');
            }

            $.each(choices, function(i, o){
                self.append('<option value="'+o.value+'">'+o.label+'</option>');
            });
        }
        function isString(obj) {
            return Object.prototype.toString.call(obj) === '[object String]';
        }

        var self = $(this);
        var loading = false;
        var model = self.data('dynamic-field-model');
        var depends = self.data('dynamic-field-depends');
        var no_value_disable = cast_python_bool_to_js(self.data('dynamic-field-no-value-disable'));
        var include_empty_choice = cast_python_bool_to_js(self.data('dynamic-field-include-empty-choice'));
        var empty_choice_label = self.data('dynamic-field-empty-choice-label');
        var callback = self.data('dynamic-field-callback');
        var initial_value = self.data('dynamic-field-default-value');
        if (isString(initial_value) && initial_value.indexOf(',') >= 0) {
            initial_value = initial_value.split(',');

        }

        if (opts.prefix && opts.index && depends.indexOf('__prefix__') >= 0) {
            depends = depends.replace('__prefix__', opts.index);
        }

        var depends_element = $('select[name='+depends+']');
        depends_element.on('change', function() {
            if ($(this).val() === '') {
                if (no_value_disable) {
                    self.prop('disabled', true);
                }
                self.empty();
            }
            else {
                if (no_value_disable) {
                    self.prop('disabled', false);
                }
                fetch_choices();
            }
        });

        if (no_value_disable && depends_element.val() === '') {
            self.prop('disabled', true);
        }

        fetch_choices(true);

        return this;
    };

    var data_attr = 'data-dynamic-field-model';
    var selector = 'select[' + data_attr + ']';
    $(document).ready(function() {
        $(selector).each(function() {
            $(this).dynamic_field();
        });
        $(document).on('DOMNodeInserted', function(e) {
            var target = $(e.target);
            if (target.find(selector)) {
                var found = target.find(selector).first();
                var prefix = null;
                var index = null;

                var total_forms = $('#id_protected_projects-3-branch')
                    .closest('fieldset')
                    .parent()
                    .find('input[name*="TOTAL_FORMS"]');

                if (total_forms.length > 0) {
                    prefix = total_forms.attr('name').replace('-TOTAL_FORMS', '');
                    index = total_forms.val();
                }

                if (found.is(selector)) {
                    found.dynamic_field({'prefix': prefix, 'index': index});
                }
            }
        });
    });
}(jQuery || django.jQuery));
