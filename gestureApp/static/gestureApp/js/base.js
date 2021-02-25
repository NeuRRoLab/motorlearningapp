// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
    el: '#navbar',
    data: () => ({
        current_user: {},
    }),
    components: {
    },
    template: `
    <div>
        <b-navbar sticky variant="light" type="light">
            <b-navbar-brand href="/">Experiment App</b-navbar-brand>

            <b-navbar-nav class="ml-auto">
                <template v-if="isObjectEmpty(current_user)">
                    <b-nav-item href="/login">Login</b-nav-item>
                    <b-nav-item href="/register">Register</b-nav-item>
                </template>
                <template v-else>
                    <b-nav-item-dropdown right>
                        <template #button-content>
                            {{current_user.username}}
                        </template>
                        <b-dropdown-item href="/profile">Profile</b-dropdown-item>
                        <b-dropdown-item href="/logout">Log Out</b-dropdown-item>
                    </b-nav-item-dropdown>
                </template>
            
            </b-navbar-nav>
        </b-navbar>
        <br>
    </div>
  `,
    methods: {
        getCurrentUser() {
            axios.get('/api/current_user').then(response => {
                this.current_user = response.data;
            })
        },
        isObjectEmpty: function (obj) {
            return Object.keys(obj).length === 0 && obj.constructor === Object;
        },
    },
    computed: {

    },
    created() {
        this.getCurrentUser();
    },
});