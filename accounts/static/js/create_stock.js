var itemDataBox = document.getElementById('item-name-on-stock-create')
$.ajax({
    type: 'GET',
    url:'/inventory/item_initial_quantity/',
    success: function(response){
        console.log(response.data)
        const itemopt = response.data
        itemopt.map(item=>{
            const option = document.createElement('div')
            // const option = document.createElement('div')
            option.textContent = item.item_name
            option.setAttribute('class', 'dropdown-item')
            option.setAttribute('data-value', item.item_name)
            itemDataBox.appendChild(option)
        })
    },

    error: function(error){
        console.log(error)
    }
})
