// color functions
function array_sorted_numeric_keys(dict_with_colors){
    var key_numeric = []
    Object.keys(dict_with_colors).forEach(k => (!isNaN(parseFloat(k)) && isFinite(k)) && key_numeric.push(parseFloat(k)));
    return key_numeric.sort(function(a, b) {return a - b;});
}

function getColor2(type, value) {
    var colors =  type == "nominal" ? colors_nominal : type == "percent"  ? colors_percent : {};
    key_numeric = array_sorted_numeric_keys(colors)
    var ret = ''
    for (const [index, v] of key_numeric.entries()) {
      if ( value <= v ) {
        var ret = colors[v]
        break;
      };
    }
    if (ret == '') {ret = colors["above"]}
    return ret
}

// legend functions
function removeElement(element) {
    element && element.parentNode && element.parentNode.removeChild(element);
}

function create_legend(layer_id){
   var legend = L.control({position: 'bottomleft'});
   legend.onAdd = function (map) {
       var div = L.DomUtil.create('div', 'info legend'),
           colors_dict = (layer_id == 27) ? colors_percent : colors_nominal,
           grades = array_sorted_numeric_keys(colors_dict),
           labels = [];
       // loop through our density intervals and generate a label with a colored square for each interval
       var type = (layer_id == 27) ? "percent" : "nominal";
       sign = type == "percent" ? '%' : ''
       for (var i = 0; i < grades.length; i++) {
            div.innerHTML +=
                '<li class="legend_items" style="background-color:' + getColor2(type, grades[i]) + '">' +
                grades[i] + (grades[i + 1] ? '&ndash;' + grades[i + 1] + sign : sign + '+') + '</li>';
       }
       div.innerHTML = '<ul>' + div.innerHTML + '</ul>'
       return div;
    };
   return legend;
}
