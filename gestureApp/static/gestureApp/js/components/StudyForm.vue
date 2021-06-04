<template>
  <div class="container">
    <h1 v-if="!editing" class="text-center">Create new Study</h1>
    <h1 v-else-if="published" class="text-center">
      View study {{ study_code }}
    </h1>
    <h1 v-else class="text-center">Edit study {{ study_code }}</h1>
    <b-form @submit="onSubmitStudy" @reset="resetStudy">
      <b-form-group label="Study Name:" label-for="name">
        <b-form-input
          name="name"
          id="name"
          v-model="study_name"
          type="text"
          required
          placeholder="Name"
          :disabled="published"
        ></b-form-input>
      </b-form-group>
      <div class="form-row">
        <b-form-group
          label="Study description:"
          label-for="description"
          class="col-6"
        >
          <b-form-textarea
            id="description"
            v-model="description"
            placeholder="Description..."
            rows="3"
            max-rows="6"
          ></b-form-textarea>
        </b-form-group>
      </div>
      <div class="form-row">
        <div class="col">
          <b-button
            type="reset"
            class="btn btn-block"
            variant="danger"
            :disabled="published"
            >Reset</b-button
          >
        </div>
        <div class="col">
          <b-button
            type="submit"
            class="btn btn-block"
            variant="primary"
            :disabled="published"
            >Submit</b-button
          >
        </div>
      </div>
    </b-form>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      study_name: this.prop_study_name,
      description: this.prop_description,
    };
  },
  props: {
    study_code: String,
    editing: Boolean,
    published: Boolean,
    prop_study_name: String,
    prop_description: String,
  },
  mounted: function () {},
  components: {
    "nav-bar": httpVueLoader("/static/gestureApp/js/components/NavBar.vue"),
  },
  computed: {},
  watch: {},
  methods: {
    onSubmitStudy(evt) {
      evt.preventDefault();

      this.$emit("submit-study", this.study_name, this.description);
    },
    resetStudy(evt) {
      evt.preventDefault();

      this.study_name = null;
    },
  },
};
</script>

<style scoped>
.block-form {
  border: 1px solid lightgray;
  padding: 10px;
}
.block-form + .block-form {
  margin-top: 10px;
}
</style>
