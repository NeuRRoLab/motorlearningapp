<!-- Component loaded on the home page of the application. Shows form to user to input the experiment they want to perform and redirects them
as appropriate. -->
<template>
  <div class="container justify-content-center">
    <div class="experiment-form">
      <b-form @submit="goToExperiment">
        <div class="form-row">
          <b-form-group class="col" label="Study Code:" label-for="study-code">
            <b-form-input
              name="code"
              id="study-code"
              v-model="study_code"
              type="text"
              :maxlength="4"
              required
              placeholder="Code"
              @input="onInputStudy"
            ></b-form-input>
          </b-form-group>
        </div>
        <div class="form-row">
          <b-form-group
            class="col"
            label="Group Code (optional):"
            label-for="group-code"
          >
            <b-form-input
              name="group-code"
              id="group-code"
              v-model="group_code"
              type="text"
              :maxlength="4"
              placeholder="Code"
              @input="onInputGroup"
            ></b-form-input>
          </b-form-group>
          <b-form-group
            class="col"
            label="Experiment Code (optional):"
            label-for="exp-code"
          >
            <b-form-input
              name="exp-code"
              id="exp-code"
              v-model="exp_code"
              type="text"
              :maxlength="4"
              placeholder="Code"
              @input="onInputExperiment"
            ></b-form-input>
          </b-form-group>
        </div>
        <b-form-group
          label="Have you done an experiment here before?"
          v-slot="{ ariaDescribedby }"
        >
          <b-form-radio-group
            id="radio-group-2"
            v-model="answer"
            :aria-describedby="ariaDescribedby"
            name="radio-sub-component"
            required
          >
            <b-form-radio :value="true">Yes</b-form-radio>
            <b-form-radio :value="false">No</b-form-radio>
          </b-form-radio-group>
        </b-form-group>
        <template v-if="answer !== null">
          <template v-if="!answer">
            <button @click="generateCode" class="btn btn-link text-primary row">
              Click here to generate subject code
            </button>
            <b-card v-if="subject_code">
              <b-card-text>
                <span class="font-weight-bold">Your Subject Code:</span>
                {{ this.subject_code }}
              </b-card-text>
              <b-card-text
                >Save this code for future studies/experiments.</b-card-text
              >
              <b-form inline>
                <label class="sr-only" for="inline-form-input-name"
                  >Email</label
                >
                <b-form-input
                  id="inline-form-input-name"
                  class="mb-2 mr-sm-2 mb-sm-0"
                  placeholder="name@example.com"
                  v-model="email"
                ></b-form-input>
                <input type="text" style="display: none" />
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
          </template>
          <div v-if="answer || subject_code.length > 0" class="form-row">
            <b-form-group
              class="col"
              id="input-group"
              label="Subject Code:"
              label-for="subj-code"
            >
              <b-form-input
                name="subj-code"
                id="subj-code"
                v-model="subject_code_input"
                type="text"
                :maxlength="subject_code_seq_length"
                placeholder="Subject Code"
                required
              ></b-form-input>
            </b-form-group>
          </div>
        </template>

        <b-button
          v-if="!logging_in"
          type="submit"
          class="btn btn-block"
          variant="primary"
          :disabled="subject_code_input.length !== subject_code_seq_length"
          >Submit</b-button
        >
        <b-button
          v-else
          type="submit"
          class="btn btn-block"
          variant="primary"
          :disabled="true"
          ><b-spinner label="Spinning"></b-spinner
        ></b-button>
      </b-form>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      study_code: "",
      group_code: "",
      exp_code: "",
      subject_code_input: "",
      email: "",
      answer: null,
      subject_code_seq_length: 16,
      logging_in: false,
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
    onInputStudy: function (input) {
      this.study_code = input.toUpperCase();
    },
    onInputGroup: function (input) {
      this.group_code = input.toUpperCase();
    },
    onInputExperiment: function (input) {
      this.exp_code = input.toUpperCase();
    },
    goToExperiment(evt) {
      evt.preventDefault();
      this.logging_in = true;
      const url = new URL(`/study/${this.study_code}/`, window.location);
      // Add params
      if (this.subject_code_input !== "")
        url.searchParams.append("subj-code", this.subject_code_input);
      if (this.group_code !== "")
        url.searchParams.append("group-code", this.group_code);
      if (this.exp_code !== "")
        url.searchParams.append("exp-code", this.exp_code);
      window.location.href = url.href;
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
  width: 730px;
  padding: 40px;
  float: none;
  margin: 0 auto;
  border-radius: 5px;
}
</style>
