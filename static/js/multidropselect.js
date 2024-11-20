$(document).ready(function(){

    $('.assign-project-PM').each(function(){
       var check = 0;
        $(this).find('.select-btn').click(function(){
            $(this).toggleClass('open');  
            var counter= 0;
            $(this).next().find('.item').each(function(){
                //  alert($(this).attr('class'));
                if ($(this).find('.checkbox .subject-expert').is(':checked'))
                {
                    counter = counter + 1;                    
                }                
            });
    
            if (counter > 0)
                    {
                        $(this).find('.btn-text').text('' + counter + ' Selected');
                    }
                    else{
                        $(this).find('.btn-text').text('Please Select');
                    }            
        });

        $(this).find('.list-items .item').each(function(){
          if ($(this).find('.checkbox .subject-expert').is(':checked'))
          {
            check += 1;
          }
        });

        if (check > 0)
        {
          $(this).find('.select-btn .btn-text').text('' + check + ' Selected');
        }
        else{
          $(this).find('select-btn .btn-text').text('Please Select');
        }
    });
});
