// Parent script that manages the relationship between the Study Form Vue component and the Django API

// CSRF token for axios
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN"

var app = new Vue({
  el: '#app',
  data: function () {
    return {
      study_code: null,
      is_study_published: false,
      study_name: null,
      description: null,
      // Whether we are creating or editing a study
      editing: false,
    }
  },
  template: `
      <div>
        <StudyForm v-bind="getStudyFormData"
          @submit-study="submitStudy"
        />
      </div>
      `,
  components: {
    'StudyForm': httpVueLoader('/static/gestureApp/js/components/StudyForm.vue'),
  },
  computed: {
    getStudyFormData() {
      return {
        study_code: this.study_code,
        editing: this.editing,
        published: this.is_study_published,
        // Study properties
        prop_study_name: this.study_name,
        prop_description: this.description,
      }
    }
  },
  methods: {
    submitStudy(name, description) {
      let obj = {
        code: this.study_code,
        name: name,
        description: description,
      }
      if (!this.editing)
        axios.post('/profile/create_study', obj).then(response =>
          window.location.href = '/profile'
        );
      else {

        axios.post(`/profile/study/edit/${this.study_code}/`, obj).then(response =>
          window.location.href = '/profile'
        );
      }
    },
  },
  created() {
    if (document.getElementById("study") !== null) {
      // If no study data is available, then we are creating a new study
      if (!JSON.parse(document.getElementById('study').textContent))
        return;
      this.editing = true;
      // Extract study information from HTML template
      html_study = JSON.parse(document.getElementById('study').textContent);
      this.study_code = html_study.code;
      this.is_study_published = html_study.published;
      this.study_name = html_study.name;
      this.description = html_study.description;
    }
  },
});

