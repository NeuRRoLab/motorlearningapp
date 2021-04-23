// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
    el: '#app',
    data: function () {
        code = JSON.parse(document.getElementById('exp_code').textContent);
        return {
            exp_code: code,
            video_url: `https://storage.googleapis.com/motor-learning/experiment_files/${code}/video.mp4`,
            pdf_url: `https://storage.googleapis.com/motor-learning/experiment_files/${code}/consent.pdf`,
        }
    },
    template: `
      <PrepScreen
        v-bind="getPrepScreenObj"
      />
      `,
    components: {
        'PrepScreen': httpVueLoader('/static/gestureApp/js/components/PreparationScreen.vue'),
    },
    computed: {
        getPrepScreenObj() {
            return {
                exp_code: this.exp_code,
                video_url: this.video_url,
                pdf_url: this.pdf_url,
            }
        }
    },
    methods: {
    },
    mounted() {
    },
});

