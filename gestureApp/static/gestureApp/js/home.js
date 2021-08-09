// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      subject_code: "",
      email_response: "",
    }
  },
  template: `
      <Home
        v-bind="getHomeObj"
        @generate-code="generateCode"
        @send-subject-code="sendEmailWithSubjectCode"
      />
      `,
  components: {
    'Home': httpVueLoader('/static/gestureApp/js/components/Home.vue'),
  },
  computed: {
    getHomeObj: function () {
      return {
        subject_code: this.subject_code,
        email_response: this.email_response,
      }
    },

  },
  methods: {
    generateCode() {
      // Do the get request and then update the subject code
      axios.get('/api/create_subject').then(response => {
        this.subject_code = response.data["subject_code"];
      })
    },
    sendEmailWithSubjectCode(email) {
      axios.post('/api/send_subject_code', {
        'subject_code': this.subject_code,
        "email": email,
      }
      ).then(response => {
        this.email_response = `Email correctly sent to ${email}.`
      }).catch(err => `Failed sending email to ${email}. ${err}`);

    }
  },
  created: function () {
  },
});

