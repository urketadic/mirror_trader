const fs = require('fs');
const config = require('./../config');

class RouteUpdate {

    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.settings = ref.settings;
        this.auth = ref.auth;
    }


    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;

        // Update settings
        app.post("/settings/update", ref.auth.do, async function (req, res) {

            //Bitmex
            ref.settings.bitmex.main.api_key = req.body.settings.bitmex.main.api_key;
            ref.settings.bitmex.main.api_secret = req.body.settings.bitmex.main.api_secret;

            //Run clients through for loop later
            ref.settings.bitmex.clients.client1.api_key = req.body.settings.bitmex.clients.client1.api_key;
            ref.settings.bitmex.clients.client1.api_secret = req.body.settings.bitmex.clients.client1.api_secret;

            let data = false;

            data = JSON.stringify(ref.settings, null, 2);
            try {
                await fs.writeFile(config['locations']['settings'], data, () => {});
            } catch (err) {
                console.log(`/settings/update: err-1 ${err}`);
            }

            // res.json({
            //     'status': 1,
            //     'message': 'saved',
            // });

        });

    }

}

module.exports = RouteUpdate;