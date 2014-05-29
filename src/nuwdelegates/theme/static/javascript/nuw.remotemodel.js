(function ($) {
    // Private vars

    var data = { length: 0 },
        base_url = 'portal_memberslistapi/',
        start = 0,
        end = 0,
        sort_column = null,
        sort_dir = null,
        search_string = null,
        search_type = null,
        page_size = 500;

    // Loading events
    var onDataLoading = new Slick.Event();
    var onDataLoaded = new Slick.Event();

    function RemoteModel() {
        function reload()
        {
            // Work out what pages to load (if any)
            var fromPage = Math.floor( start / page_size );
            var toPage = Math.floor( end / page_size );
            var totalPages = Math.floor( ( data.length / page_size ) )

            if ( fromPage > 0 )
                fromPage -= 1;

            if ( toPage < totalPages )
                toPage += 1;

            // Check if any pages need to be unloaded
            if ( fromPage - 1 > 0 && fromPage - 1 < totalPages && isPageLoaded( fromPage - 2 ) )
                unloadPage( fromPage - 2 );

            if ( toPage + 1 > 0 && toPage + 1 < totalPages && isPageLoaded( toPage + 2 ) )
                unloadPage( toPage + 2 );

            // Reduce pages that need to be loaded if they are already loaded
            while ( fromPage < toPage && isPageLoaded( fromPage ) )
                fromPage += 1;

            while ( fromPage < toPage && isPageLoaded( toPage ) )
                toPage -= 1;

            if ( fromPage > toPage || fromPage == toPage && isPageLoaded( fromPage ) )
                return;

            // Set first entry in each page to a loading indicator to prevent the page from being loaded twice etc.
            for ( var pg = fromPage; pg <= toPage; pg++ )
            {
                data[ pg * page_size ] = { id: 'loading' };
            }

            var from = fromPage * page_size,
                to = ( toPage + 1 ) * page_size;

            onDataLoading.notify( { from: from, to: to } )

            var query = {
                start: from,
                end: to
            };
            if ( sort_column !== null )
                query.sort_column = sort_column;
            if ( sort_dir !== null )
                query.sort_dir = sort_dir;
            if ( search_string !== null )
                query.search_string = search_string;
            if (search_type !== null) {
                query.search_type = search_type;
            }

            /* Will fetch the data */
            $.ajax( {
                url: base_url + 'get_members',
                type: 'POST',
                dataType: 'json',
                data: query,
                success: function ( ret ) {
                    data.length = ret.total;

                    for ( var i = 0; i < ret.members.length; i++ )
                    {
                        data[ from + i ] = ret.members[ i ];
                        data[ from + i ].index = from + i;
                    }

                    onDataLoaded.notify( { from: from, to: from + ret.members.length, members: ret.member_total } );
                }
            } );
        }

        function clear()
        {
            for ( var key in data )
            {
                delete data[key];
            }

            data.length = 0;
        }

        function unloadPage( pagenr )
        {
            // Calculate what rows to unload
            var from = pagenr * page_size,
                to = ( pagenr + 1 ) * page_size;

            for ( var i = from; i < to; i++ )
            {
                delete data[ i ];
            }
        }

        function isPageLoaded( pagenr )
        {
            // Assumes that if the first row in a page has data it is loaded
            if ( data[ pagenr * page_size ] !== undefined )
                return true;

            return false;
        }

        function setViewport( top, bottom )
        {
            start = top;
            end = bottom;
            //page_size = end - start;
        }

        function setSortColumn( column, dir )
        {
            sort_column = column;
            sort_dir = dir;
        }

        function setFilter(search, stype)
        {
            search_string = search;
            search_type = stype;
        }

        return {
            // properties
            "data": data,

            // methods
            "clear": clear,
            "reload": reload,
            "setFilter": setFilter,
            "setSortColumn": setSortColumn,
            "setViewport": setViewport,

            // Events
            "onDataLoading": onDataLoading,
            "onDataLoaded": onDataLoaded
        };
    }


    // Slick.Data.RemoteModel
    $.extend(true, window, { NUW: { Data: { RemoteModel: RemoteModel }}});
})(jQuery);
