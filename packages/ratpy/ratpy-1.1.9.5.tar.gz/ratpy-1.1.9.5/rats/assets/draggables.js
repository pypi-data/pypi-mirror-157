if (!window.dash_clientside) {
    window.dash_clientside = {};
}

window.dash_clientside.clientside = {

    make_draggable: function () {
        const draggables = document.querySelectorAll('.rats-card')
        const containers = document.querySelectorAll('.rats-card-group')

        //    handle class addition and removal on drag events
        draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', () => {
                draggable.classList.add('dragging')
            })

            draggable.addEventListener('dragend', () => {
                draggable.classList.remove('dragging')
            })
        })

        //    Add an event listener for when something is being dragged over one of the containers
        containers.forEach(container => {
            container.addEventListener('dragover', e => {
                e.preventDefault()

                const draggableElements = [...container.querySelectorAll('.rats-card:not(.dragging)')]

                const afterElement = getDragAfterElement(draggableElements, e.clientX)

                const draggable = document.querySelector('.dragging')
                if (afterElement == null) {
                    container.appendChild(draggable)
                } else {
                    container.insertBefore(draggable, afterElement)
                }
            })
        })

        function getDragAfterElement(draggableElements, x) {
            return draggableElements.reduce((closest, child) => {
                const box = child.getBoundingClientRect()
                const offset = x - (box.left + box.width / 2)
                if (offset < 0 && offset > closest.offset) {
                    return {offset: offset, element: child}
                } else {
                    return closest
                }
            }, {offset: Number.NEGATIVE_INFINITY}).element
        }

        return window.dash_clientside.no_update}
}






