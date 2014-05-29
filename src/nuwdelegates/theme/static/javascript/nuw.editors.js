(function ($) {
    $.extend(true, window, {
        "NUW": {
            "Editors": {
                "SelectEditor": SelectEditor,
                'NameEditor': NameEditor,
                'AddressEditor': AddressEditor
            }
        }
    });

    function SelectEditor( args ) {
        var $input;
        var defaultValue;
        var selectValues = {};
        var scope = this;

        this.init = function () {
            var html = '<select>';

            selectValues = args.column.selectValues;

            if ( typeof selectValues == 'function' )
            {
                selectValues = selectValues( args );
            }

            if ( selectValues instanceof Array )
            {
                var nsv = {};
                for ( idx in selectValues )
                {
                    val = selectValues[ idx ];

                    nsv[ val ] = val;
                }
                selectValues = nsv;
            }

            for ( key in selectValues )
            {
                val = selectValues[ key ];

                html += '<option value="' + key + '">' + val + '</option>';
            }

            html += '</select>';

            $input = $( html )
                .appendTo(args.container)
                .bind( "keydown", this.handleKeyDown )
                .focus();
        };

        this.handleKeyDown = function ( e ) {
            if ( e.keyCode === $.ui.keyCode.UP || e.keyCode === $.ui.keyCode.DOWN || e.keyCode === $.ui.keyCode.LEFT || e.keyCode === $.ui.keyCode.RIGHT )
            {
                e.stopImmediatePropagation();
            }
        }

        this.loadValue = function ( item ) {
            defaultValue = item[args.column.field] || "";
            $input.val(defaultValue);
            $input[0].defaultValue = defaultValue;
        }

        this.serializeValue = function () {
            return $input.val();
        };

        this.isValueChanged = function () {
            return (!($input.val() == "" && defaultValue == null)) && ($input.val() != defaultValue);
        };

        this.validate = function () {
            if (args.column.validator) {
                var validationResults = args.column.validator($input.val());
                if (!validationResults.valid) {
                    return validationResults;
                }
            }

            return {
                valid: true,
                msg: null
            };
        };

        this.applyValue = function (item, state) {
            item[args.column.field] = state;
        };

        this.destroy = function () {
            $input.remove();
        };

        this.focus = function () {
            $input.focus();
        };

        this.getValue = function () {
            return $input.val();
        };

        this.setValue = function (val) {
            $input.val(val);
        };


        this.init();
    }

    function NameEditor( args )
    {
        //Inputs
        var $firstname, $preferredname, $lastname, $title, $wrapper;

        var scope = this;

        var title_values = { null: '', 'Ms': 'Ms', 'Miss': 'Miss', 'Mrs': 'Mrs', 'Mr': 'Mr' };

        this.init = function () {
            var $container = $("body");

            $wrapper = $('<div style="z-index:10000;position:absolute;background:white;padding:5px;border:3px solid gray; -moz-border-radius:10px; border-radius:10px;"/>')
                .bind( "keydown", this.handleKeyDown )
                .appendTo( $container );

            var html = '<select>';

            for ( key in title_values )
            {
                val = title_values[ key ];

                html += '<option value="' + key + '">' + val + '</option>';
            }

            html += '</select>';

            $title = $( html )
                .appendTo( $wrapper );

            $firstname = $( '<input type="text" />' )
                .appendTo( $wrapper );

            $lastname = $( '<input type="text" />' )
                .appendTo( $wrapper );

            $( '<br /><span>Preferred Name: </span>' ).appendTo( $wrapper );
            $preferredname = $( '<input type="text" />' )
                .appendTo( $wrapper );


            $('<div style="text-align:right"><button>Save</button><button>Cancel</button></div>')
                .appendTo( $wrapper );

            $wrapper.find( "button:first" ).bind( "click", this.save );
            $wrapper.find( "button:last" ).bind( "click", this.cancel );

            scope.position( args.position );

            $firstname.focus();
        }

        this.handleKeyDown = function ( e ) {
            if ( e.keyCode == $.ui.keyCode.ESCAPE )
                scope.cancel();
            else if ( e.keyCode == $.ui.keyCode.ENTER )
                scope.save();
        }

        this.loadValue = function ( item ) {
            $title.val( item.title );
            $firstname.val( item.firstname );
            $lastname.val( item.lastname );
            if ( item.firstname != item.preferredname )
                $preferredname.val( item.preferredname );
            else
                $preferredname.val( '' );
        }

        this.serializeValue = function () {
            var ret = {
                firstname: $firstname.val(),
                lastname: $lastname.val(),
                preferredname: ( $preferredname.val() == '' ? $firstname.val() : $preferredname.val() )
            }, title = $title.val();

            if ( title !== 'null' )
            {
                ret.title = title;
            }
            return ret;
        }

        this.isValueChanged = function () {
            return args.item.title != $title.val() || args.item.firstname != $firstname.val() ||
                args.item.lastname != $lastname.val() || args.item.preferredname != $preferredname.val();
        };

        this.validate = function () {
            // TODO
            /*if (args.column.validator) {
                var validationResults = args.column.validator($input.val());
                if (!validationResults.valid) {
                    return validationResults;
                }
            }*/

            return {
                valid: true,
                msg: null
            };
        };

        this.applyValue = function (item, state) {
            item.title = state.title;
            item.firstname = state.firstname;
            item.lastname = state.lastname;
            item.preferredname = state.preferredname;
        };

        this.position = function (position) {
            /* Make sure entire editor is always visible */
            var winh = $( window ).innerHeight(), wrah = $wrapper.outerHeight(),
                gridsize = grid.getGridPosition();

            if ( position.top - 5 + wrah > winh )
                position.top -= position.top - 5 + wrah - winh;
            else if ( position.top - 5 < gridsize.top )
                position.top = gridsize.top + 5;

            $wrapper
                .css( "top", position.top - 5 )
                .css( "left", position.left - 5 );
        };

        this.destroy = function () {
            $wrapper.remove();
        };

        this.save = function () {
            args.commitChanges();
        };

        this.cancel = function () {
            args.cancelChanges();
        };

        this.init();
    }

    function AddressEditor( args )
    {
        //Inputs
        var $addr1, $addr2, $suburb, $state, $pcode;

        var scope = this;

        var prefix = '';

        this.init = function () {
            prefix = args.column.addrPrefix;

            var $container = $("body");

            $wrapper = $('<div style="z-index:10000;position:absolute;background:white;padding:5px;border:3px solid gray; -moz-border-radius:10px; border-radius:10px;"/>')
                .bind( "keydown", this.handleKeyDown )
                .appendTo( $container );

            $addr1 = $( '<input type="text" style="width: 98%" placeholder="Address" /><br />' )
                .appendTo( $wrapper );

            $addr2 = $( '<input type="text" style="width: 98%" placeholder="Address" /><br />' )
                .appendTo( $wrapper );

            $suburb = $( '<input type="text" style="width: 150px" placeholder="Suburb" />' )
                .appendTo( $wrapper );

            var html = '<select>';
            for ( idx in state_values )
            {
                val = state_values[ idx ];

                html += '<option value="' + val + '">' + val + '</option>';
            }
            html += '</select>';
            $state = $( html )
                .appendTo( $wrapper );

            $pcode = $( '<input type="text" style="width: 80px" placeholder="Post Code" />' )
                .appendTo( $wrapper );

            $('<div style="text-align:right"><button>Save</button><button>Cancel</button></div>')
                .appendTo( $wrapper );

            $wrapper.find( "button:first" ).bind( "click", this.save );
            $wrapper.find( "button:last" ).bind( "click", this.cancel );

            scope.position( args.position );

            $addr1.focus();
        }

        this.handleKeyDown = function ( e ) {
            if ( e.keyCode == $.ui.keyCode.ESCAPE )
                scope.cancel();
            else if ( e.keyCode == $.ui.keyCode.ENTER )
                scope.save();
        }

        this.loadValue = function ( item ) {
            $addr1.val( item[ prefix + 'address1' ] );
            $addr2.val( item[ prefix + 'address2' ] );
            $suburb.val( item[ prefix + 'suburb' ] );
            $state.val( item[ prefix + 'state' ] );
            $pcode.val( item[ prefix + String(prefix == 'post' ? 'pcode' : 'postcode') ] );
        }

        this.serializeValue = function () {
            var ret = {
                addr1: $addr1.val(),
                addr2: $addr2.val(),
                suburb: $suburb.val(),
                state: $state.val(),
                pcode: $pcode.val()
            };

            return ret;
        }

        this.isValueChanged = function () {
            return args.item[ prefix + 'address1' ] != $addr1.val() || args.item[ prefix + 'address2' ] != $addr2.val() ||
                args.item[ prefix + 'suburb' ] != $suburb.val() || args.item[ prefix + 'state' ] != $state.val() ||
                args.item[ prefix + 'pcode' ] != $pcode.val();
        };

        this.validate = function () {
            return {
                valid: true,
                msg: null
            };
        };

        this.applyValue = function (item, state) {
            item[ prefix + 'address1' ] = state.addr1;
            item[ prefix + 'address2' ] = state.addr2;
            item[ prefix + 'suburb' ] = state.suburb;
            item[ prefix + 'state' ] = state.state;
            if ( prefix == 'post' )
                item[ 'postpcode' ] = state.pcode;
            else
                item[ 'homepostcode' ] = state.pcode;
        };

        this.position = function (position) {
            /* Make sure entire editor is always visible */
            var winh = $( window ).innerHeight(), wrah = $wrapper.outerHeight(),
                gridsize = grid.getGridPosition();

            if ( position.top - 5 + wrah > winh )
                position.top -= position.top - 5 + wrah - winh;
            else if ( position.top - 5 < gridsize.top )
                position.top = gridsize.top + 5;

            $wrapper
                .css( "top", position.top - 5 )
                .css( "left", position.left - 5 );
        };

        this.destroy = function () {
            $wrapper.remove();
        };

        this.save = function () {
            args.commitChanges();
        };

        this.cancel = function () {
            args.cancelChanges();
        };

        this.init();
    }

})(jQuery);
