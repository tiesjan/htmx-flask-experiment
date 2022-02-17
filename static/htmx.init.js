'use strict';

window.addEventListener('load', function(event) {
    // Error handling
    document.body.addEventListener('htmx:beforeSwap', function(event) {
        // Allow error pages to be swapped in for certain HTTP status codes
        const allowedStatuses = [400, 404];
        if (allowedStatuses.indexOf(event.detail.xhr.status) !== -1) {
            event.detail.shouldSwap = true;
            event.detail.isError = false;
        }
    });

    // Extensions
    htmx.defineExtension('destroy-element', {
        onEvent: function (name, event) {
            if (name === 'htmx:afterProcessNode') {
                const element = event.detail.elt;

                // Parse timeout, if set
                let destroyTimeout = 0;
                if ('destroyTimeout' in element.dataset) {
                    destroyTimeout = htmx.parseInterval(
                        element.dataset['destroyTimeout']
                    );
                }

                // Remove element after parsed timeout
                setTimeout(
                    function() { element.parentElement.removeChild(element); },
                    destroyTimeout
                );
            }
        }
    });

    htmx.defineExtension('disable-submit-buttons', {
        onEvent: function (name, event) {
            // Find submit buttons
            const submitButtons = htmx.findAll(
                '.submit-buttons > button, .submit-buttons > input[type="submit"]'
            );

            // Disable all submit buttons during requests
            for (let i = 0; i < submitButtons.length; i++) {
                if (name === 'htmx:beforeRequest') {
                    submitButtons[i].disabled = true;
                }
                else if (name === 'htmx:afterRequest') {
                    submitButtons[i].disabled = false;
                }
            }
        }
    });

    htmx.defineExtension('mark-selected', {
        onEvent: function(name, event) {
            // Mark elements when contact details are loaded
            if (name === 'htmx:afterOnLoad') {
                htmx.takeClass(event.detail.elt, 'selected');
            }
            // Mark elements when they have 'data-mark-selected' set to 'true'
            else if (name === 'htmx:load' &&
                    event.detail.elt.dataset['markSelected'] === 'true') {
                htmx.takeClass(event.detail.elt, 'selected');
                delete event.detail.elt.dataset['markSelected']
            }
        }
    });
});
