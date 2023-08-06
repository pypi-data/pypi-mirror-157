import ValidationHelper from '/webui/static/zjs/validation_helper.js'; //
import WCMaster from  '/webui/static/zwc/wc_master.js' ;


class WCGroup extends WCMaster  { 
    define_template(){
        return super.define_template() + ` 
                <div class="container">

                    <div class="m-3 ${ this._inp['bordered']?'box':''} p-3" id="si_field">
                        <slot>
                        </slot>
                         
                        <xnav class="level">
                            <div class="container mt-6 xlevel-right">
                                <div class="xlevel-item has-text-centered is-pulled-right"> 
                                    <p class="control "> 
                                        <wc-button id="sci_site_save" label="Save" 
                                            action="/"
                                            submit_data_selector=".sck_site_cnf_validate" 
                                            popup_message_submit_success="Site Added"
                                            popup_message_submit_fail="Internal error in adding new site"
                                        ></wc-button> 
                                        <wc-button id="sci_site_cancel" label="Cancel" active_class="none" > </wc-button>  
                                        <wc-button id="sci_site_delete" label="Delete" active_class="is-danger"
                                            action="{#{ url_for( 'siteadmin.site_delete_ajax') }#}"
                                            submit_data_selector="#si_site_id"  > </wc-button> 
                                            <!-- , site_id=site_data.id) -->
                                    </p>  
                                </div>
                            </div>
                        </xnav>
                         
                        
                    </div>   

                </div>`
    } 

    constructor( ) {
        super( {"bordered=bool":true}, ["id"]); 
    }

    init_component(){}
    
    hide(){
        this.shadowRoot.querySelector('#si_field').classList.add('is-hidden');
        const event = new CustomEvent('group_disappear', { detail: {this:this  }} );
        this.dispatchEvent(event , { bubbles:true, component:true} ); 
    }

    show(){
        this.shadowRoot.querySelector('#si_field').classList.remove('is-hidden');

        console.log("trigger group appear [0]:" + this.id )
        const event = new CustomEvent('group_appear', { detail: {this:this  }} );
        this.dispatchEvent(event , {bubbles:true,component:true } ); 
        console.log("trigger group appear [1]:" + this.id )
    }
}

window.customElements.define('wc-group', WCGroup); 



