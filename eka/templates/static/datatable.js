/**
 * 
 */
$(document).ready(function () {
  $("#table_informative").DataTable({
	  "order": [[ 3, "desc" ]],
	  "lengthChange": false,
	  "pageLength": 10
  });
  
  $("#table_distinct").DataTable({
	  "order": [[ 3, "desc" ]],
	  "lengthChange": false,
	  "pageLength": 10
  });
  
  $("#table_details").DataTable({
	  "lengthChange": false,
	  "paging":   false,
      "ordering": false,
      "searching": false,
      "info": false
  });
  
  $("#table_results").DataTable({
	  "lengthChange": true,
	  "pageLength": 25
  });
  
  $("#table_results1").DataTable({
	  "lengthChange": true,
	  "pageLength": 25
  });

  var reason = 0;
  
  
  $("#addControl").click(function() {
	  
      if (reason < 8) {
    	  reason = reason + 1;
    	  var template = '<div class="input-group" id="div'+reason+'">'+
			'<select name="category'+reason+'" class="form-control" id="cat'+reason+'">	<option value="00" selected>Choose one category</option>'+
			 ' <option value="01">Electric Wheelchair and wheelchair user</option>'+
			 ' <option value="03">Mobility impaired person</option>'+
			  '<option value="04">Ashtma and breathing issues</option>'+
			 ' <option value="05">Visually impaired person</option>'+
			 ' <option value="06">Dyslexic and orientation disorders</option>'+
			 ' <option value="07">Learning difficulty and autism</option>'+
			 ' <option value="08">Mental Health problems</option>'+
			 ' <option value="09">Dexterity problems</option>'+
			 ' <option value="10">Hearing impaired person</option> {% endfor %} </select>'+
			 '<span class="input-group-btn"> <button id="remove'+reason+'" class="btn btn-primary remove-me" type="button">-</button> </span> </div>';

          // Add select
    	  var temp = $(template).appendTo("#dynamic");
    	  
      }
      // AFTER REACHING THE SPECIFIED LIMIT, DISABLE THE "ADD" BUTTON.
      // (20 IS THE LIMIT WE HAVE SET)
      else {      
    	  var message = "<label>Reached the limit</label>";
    	  var temp = $(message).appendTo("#dynamic");
      }
	    
  });
  
  $('#dynamic').on('click', '.remove-me', function(){
	  var fieldNum = this.id.charAt(this.id.length-1);
	  var divID = '#div'+fieldNum;

	  $(divID).remove();
	  reason = reason - 1;
	  
	});

  console.log( "ready!" );
});