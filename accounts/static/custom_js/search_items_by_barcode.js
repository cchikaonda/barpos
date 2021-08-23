
const searchField = $("#searchField");

const searchProducts = $(".searched-output-products");
searchProducts.style.display = "none";

const allProducts = $(".table-all-products");

const tablebody= $(".searchtable-tbody");

searchField.addEventListener("keyup", (e) => {
    const searchValue = e.target.value;
    if (searchValue.trim().length > 0){
        console.log('searchValue', searchValue);
        tablebody.innerHTML = "";
        fetch("/pos/search_item", {
            body: JSON.stringify({searchText: searchValue}),
            method: "POST",
        })
       .then((res) => res.json())
       .then((data) => {
           console.log("data", data);
           allProducts.style.display = "none";
           searchProducts.style.display = "block";
         
           if(data.length===0){
               searchProducts.innerHTML="No Item Found!!";
           }else{
               data.forEach((item) => {
                   //Use the tempral literal not the '' but ``
                   tablebody.innerHTML+= `
                   <tr style="height: 70px; font-size: x-large;" class="clickable-row" data-href="add_to_cart/${item.slug}"> 
                   <td>${item.id}</td> 
                   <td><a href = "add_to_cart/${item.slug}">${item.item_name} </a></td> 
                   <td><a href = "add_to_cart/${item.slug}">${item.barcode}</a></td> 
                   <td><a href = "add_to_cart/${item.slug}">${item.item_description}</a></td> 
                   <td><a href = "add_to_cart/${item.slug}">${item.price_currency} ${item.price}</a></td> 
                   </tr>`;  
                    
               });
               
           }
        });
    }else{
       
        allProducts.style.display = "block";
        searchProducts.style.display = "none"
        

           }

       });
    