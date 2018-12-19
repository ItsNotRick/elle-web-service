$(function(){
	$('#btnOne').click(function(){

		$.ajax({
			url: '/logout',
			headers: {'Authorization':localStorage.getItem('head'),'Content-Type':'application/json'},
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

$(function(){
	$('#btnTwo').click(function(){
		
		$.ajax({
			url: '/deck/game/300',
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

$(function(){
	$('#btnThree').click(function(){
		
		$.ajax({
			url: '/deck/zip/300',
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});

$(function(){
	$('#btnFour').click(function(){
		
		$.ajax({
			url: '/login',
			type: 'GET',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});