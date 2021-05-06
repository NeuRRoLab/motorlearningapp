<template>
  <div class="container justify-content-center">
    <div class="experiment-form">
      <b-form @submit="goToExperiment">
        <div class="form-row">
          <b-form-group
            class="col"
            id="input-group"
            label="Experiment Code:"
            label-for="input"
          >
            <b-form-input
              name="code"
              id="input"
              v-model="experiment_code"
              type="text"
              :maxlength="4"
              required
              placeholder="Code"
              @input="onInput"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col"
            id="input-group"
            label="Subject Code (optional):"
            label-for="subj-code"
          >
            <b-form-input
              name="subj-code"
              id="subj-code"
              v-model="subject_code_input"
              type="text"
              :maxlength="16"
              placeholder="Subject Code"
            ></b-form-input>
          </b-form-group>
        </div>
        <button
          v-if="!subject_code"
          @click="generateCode"
          class="btn btn-link text-primary row"
        >
          Generate subject code
        </button>
        <b-card v-else>
          <b-card-text>
            <span class="font-weight-bold">Your Subject Code:</span>
            {{ this.subject_code }}
          </b-card-text>
          <b-card-text>Save this code for future experiments.</b-card-text>
          <b-form inline>
            <label class="sr-only" for="inline-form-input-name">Email</label>
            <b-form-input
              id="inline-form-input-name"
              class="mb-2 mr-sm-2 mb-sm-0"
              placeholder="name@example.com"
              v-model="email"
            ></b-form-input>
            <b-button
              variant="primary"
              @click="
                $emit('send-subject-code', email);
                email = '';
              "
              >Send code to email</b-button
            >
          </b-form>
          <b-card-text v-if="email_response !== ''">{{
            email_response
          }}</b-card-text>
        </b-card>
        <br />

        <b-button type="submit" class="btn btn-block" variant="primary"
          >Submit</b-button
        >
      </b-form>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      experiment_code: "",
      subject_code_input: "",
      email: "",
    };
  },
  props: {
    subject_code: String,
    email_response: String,
  },
  mounted: function () {},
  components: {
    "nav-bar": httpVueLoader("/static/gestureApp/js/components/NavBar.vue"),
  },
  computed: {},
  watch: {
    subject_code: function (newVal, oldVal) {
      this.subject_code_input = newVal;
    },
  },
  methods: {
    onInput: function (input) {
      this.experiment_code = input.toUpperCase();
    },
    goToExperiment(evt) {
      evt.preventDefault();
      window.location.href = `/experiment/${this.experiment_code}/?subj-code=${this.subject_code_input}`;
    },
    generateCode(evt) {
      evt.preventDefault();
      this.$emit("generate-code");
    },
  },
};
</script>

<style scoped>
.experiment-form {
  border: 1px solid lightgray;
  width: 530px;
  padding: 40px;
  float: none;
  margin: 0 auto;
  border-radius: 5px;
}
</style>
