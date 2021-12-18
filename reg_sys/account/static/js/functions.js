/*
Developed by David Harris

This contains functions used throughout the registration system.

$_TimeMod is for creating times within the new course/modified course sections of the website.
$_TermMod is for creating new terms within the new cours/emodified course sections of the website.

Both functions use HTML data, such as forms, buttons, div's, and spans. All of these must 
be properly set and labeled before using the below functions. For $_TimeMod you can 
specify the name of the forms by modifying the variables inside of $_TimeMod before 
calling the methods. TO DO: But $_TermMod's reference to the HTML documents cannot yet be 
externally modified -- needs restructring to be more like $_TimeMod
*/

	$_TimeMod = {
		days: {},
		radioBtn:"days",
		start_time:"class_start_time",
		end_time:"class_end_time",
		type_of_class:"type_of_class_time",
		time_box:"times",
		form_input_box:"class_times",
		//Sets time for when page is loaded, e.g., whem modifying a course 
		//the Django template passes an array with times in it
		setTime: function(array){
			this.days=array;
			for (var day in this.days) {
				for (var time in this.days[day])
				{
					this.addTimeBox(day,time,this.days[day][time][0],this.days[day][time][1],
					this.days[day][time][2]);
				}	
			}
		},
		//Add a time for when user clicks the add time button
		addTime: function(){
			
			//Check validity
			var valid=true;
			var reg=/\d\d:\d\d:\d\d/;
			if ( ! reg.test($("#"+this.start_time).val()) ) 
				valid=false;
			reg=/\d\d:\d\d:\d\d/;
			if ( ! reg.test($("#"+this.end_time).val()) ) 
				valid=false;
			
			if (!valid){
				alert("Invalid times.");
				return false;
			}
			
			//this ref. is needed for jquery's for each. turns out reference is
			//lost when entering it (use 'this' inside of it refers to different scope)
			ref=this;
			
			//for each 'day' box...
			$("input[name='"+this.radioBtn+"']").each(function(){
				//if checked...
				if ($(this).prop('checked')==true){
					//get the checked value (e.g., monday, tuesday)
					var day=$(this).val();
					//get the start/endtime (e.g., 14:20), and whether classroom/lab
					var time = [
						$("#"+ref.start_time).val(),
						$("#"+ref.end_time).val(),
   						$("input[name='"+ref.type_of_class+"']:checked").val()];
					//may be undefined, so...
					if (typeof ref.days[day] === 'undefined')
						ref.days[day] = [];
					//add the date and time to the days array
					ref.days[day].push(time);
					//uncheck it to 'refresh' the add time feature 
					$(this).prop('checked',false);
					//add label + onclick for removing this element
					ref.addTimeBox(day,(ref.days[day].length-1),time[0],time[1],time[2]);
				}
			});
		},
		addTimeBox : function(day,time,start,end,type){
   			var string="<span id='"+day+time+"' "
   			+" onclick='$_TimeMod.removeTime(\""+day+"\",\""+time+"\")' "
   			+ "class='label label-info'>"+day+" "+start+" - "+end+" ("+type+")</span>&nbsp;";
   			$("#"+this.time_box).append(string);
   			$("#"+this.form_input_box).val(JSON.stringify(this.days));
		},
		removeTime: function (day,time){
			//set to [] so that array length is maintained
			//otherwise removing the element will mess up
			//other removals will get messed up
			this.days[day][time]=[];
			$("#"+this.form_input_box).val(JSON.stringify(this.days));
			$("#"+day+time).remove();
		}
   }
   
   $_TermMod={
		//Send new term data via ajax, get in return the ID number from database.
		//This ID allows us to add to thew "term" selection box
		newTerm: function(){
			
			//Check validity
			var valid=true;
			var reg=/\d\d\d\d/;
			
			if ( $("#term_name").val().length < 1)
				valid=false;
			
			if ( ! reg.test($("#term_year").val()) ) 
				valid=false
			
			reg= /\d\d\d\d-\d\d-\d\d/;			
			if ( ! reg.test($("#reg_start_date").val()) ) 
				valid=false
			
			reg= /\d\d\d\d-\d\d-\d\d/;	
			if ( ! reg.test($("#reg_end_date").val()) ) 
				valid=false
			
			reg= /\d\d\d\d-\d\d-\d\d/;	
			if ( ! reg.test($("#withdrawal_date").val()) ) 
				valid=false	
			
			if (!valid){
				alert("Invalid entries for creating new term.");
				return false;
			}
			
			$.ajax({
				type: 'POST',
				url: '/new_term',
				data: {
					//For data
					term_name:$("#term_name").val(),
					term_year:$("#term_year").val(),
					reg_start_date:$("#reg_start_date").val(),
					reg_end_date:$("#reg_end_date").val(),
					withdrawal_date:$("#withdrawal_date").val(),
					//Django verification
					csrfmiddlewaretoken:$("[name=csrfmiddlewaretoken]").val()
				},
				dataType:'json',
				success: function(response)
				{
					if (response.success){
						$("[name=term_id]").append("<option value='"
						+response.id+"' selected='selected'>"
						+response.name + " " + response.year+"</option>");
						$("#new_term_div").hide();
					}
					else
						alert(response.error);
				}
			});
		}
   }
   
    $_CourseMod={
		//Send new term data via ajax, get in return the ID number from database.
		//This ID allows us to add to thew "term" selection box
		newCourse: function(){
			
			//Check validity
			var valid=true;
			var reg=/\d\d\d\d/;
			
			if ( $("#course_name").val().length < 1)
				valid=false;
			if ( $("#course_subject").val().length < 1)
				valid=false;
			if ( $("#course_name_id").val().length < 1)
				valid=false;
			
			/* #course_department .... should validate this too*/
			
			if (!valid){
				alert("Invalid entries for creating new course.");
				return false;
			}
			
			$.ajax({
				type: 'POST',
				url: '/new_course',
				data: {
					//For data
					course_description:$("#course_description").val(),
					course_name:$("#course_name").val(),
					course_name_id:$("#course_name_id").val(),
					course_subject:$("#course_subject").val(),
					course_department:$("#course_department").val(),
					course_prerequisites:$("#course_prerequisites").val(),
					//Django verification
					csrfmiddlewaretoken:$("[name=csrfmiddlewaretoken]").val()
				},
				dataType:'json',
				success: function(response)
				{
					if (response.success){
						$("[name=course_id]").append("<option value='"
						+response.id+"' selected='selected'>"
						+$("#course_name_id").val() + "</option>");
						$("#new_course_div").hide();
					}
					else
						alert(response.error);
				}
			});
		}
   }