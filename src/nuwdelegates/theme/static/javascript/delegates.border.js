jQuery( window ).load( function () {
    $( window ).resize( function () {
        /* Resize the grid to fill the window */
        if ( $( 'body.template-sitelist' ).length )
        {
            var window_width = $( window ).width(),
                window_height = $( window ).height(),
                sidenav_width = $( '#portal-column-one' ).outerWidth( true ),
                header_height = $( '#header-container' ).outerHeight( true ),
                footer_height = $( '#footer-container' ).outerHeight( true );
                
            $( '#portal-column-one,#portal-column-content' ).css( 'height', window_height - header_height - footer_height );
            $( '#portal-column-content' ).css( 'width', window_width - sidenav_width );
            
            $( '#grid' ).css( 'height', window_height - header_height - footer_height - $( '#grid-header' ).outerHeight( true ) );
            
            if ( grid != undefined )
                grid.resizeCanvas();
        }
        
        /* Make sure sidenav is as high as the highest column */
        if ( $( '#portal-column-one *' ).length )
        {
            var sidenav_height = $( '#portal-column-one' ).outerHeight( true ),
                rcol_height = $( '#portal-column-two' ).outerHeight( true ),
                content_height = $( '#portal-column-content' ).outerHeight( true ),
                $navportlet = $( '#nuw-navigation-portlet' );
            
            if ( content_height > sidenav_height )
            {
                sidenav_height = content_height;
            }
            if ( rcol_height > sidenav_height )
            {
                sidenav_height = rcol_height;
            }

            $( '#portal-column-one' ).css( 'height', sidenav_height );
            
            $navportlet.css( 'height', $( '#portal-column-one' ).outerHeight( true )
                    - parseInt( $navportlet.css( 'padding-top' ) )
                    - parseInt( $navportlet.css( 'padding-bottom') )
                    - $( '#portal-column-one .managePortletsLink' ).outerHeight( true ) );
        }
    } ).resize();
} );


