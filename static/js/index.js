function changeColor(num){
    var pre_k = document.getElementById("pre-k")
    var grade_k = document.getElementById("grade-k")
    var grade_1 = document.getElementById("grade-1")
    var grade_2 = document.getElementById("grade-2")
    //pre_k.style.backgroundColor="LightGray"

    if(num == 1){
        $("#pbar_pre_k").addClass("progress-bar-animated")
        $("#pbar_k").removeClass("progress-bar-animated")
        $("#pbar_1").removeClass("progress-bar-animated")
        $("#pbar_2").removeClass("progress-bar-animated")
        pre_k.style.border="3px solid black"
        grade_k.style.border="1px solid black"
        grade_1.style.border="1px solid black"
        grade_2.style.border="1px solid black"
    }else if(num == 2){
        $("#pbar_pre_k").removeClass("progress-bar-animated")
        $("#pbar_k").addClass("progress-bar-animated")
        $("#pbar_1").removeClass("progress-bar-animated")
        $("#pbar_2").removeClass("progress-bar-animated")
        pre_k.style.border="1px solid black"
        grade_k.style.border="3px solid black"
        grade_1.style.border="1px solid black"
        grade_2.style.border="1px solid black"
    }else if(num == 3){
        $("#pbar_pre_k").removeClass("progress-bar-animated")
        $("#pbar_k").removeClass("progress-bar-animated")
        $("#pbar_1").addClass("progress-bar-animated")
        $("#pbar_2").removeClass("progress-bar-animated")
        pre_k.style.border="1px solid black"
        grade_k.style.border="1px solid black"
        grade_1.style.border="3px solid black"
        grade_2.style.border="1px solid black"
    }else{
        $("#pbar_pre_k").removeClass("progress-bar-animated")
        $("#pbar_k").removeClass("progress-bar-animated")
        $("#pbar_1").removeClass("progress-bar-animated")
        $("#pbar_2").addClass("progress-bar-animated")
        pre_k.style.border="1px solid black"
        grade_k.style.border="1px solid black"
        grade_1.style.border="1px solid black"
        grade_2.style.border="3px solid black"
    }
    
        
    
}

