<template>
  <div v-if="!isUserEmpty" class="container">
    <h1 class="text-center">Profile</h1>
    <template v-if="unpublished_experiments.length > 0">
      <h4>Unpublished experiments:</h4>
      <b-list-group class="col">
        <b-list-group-item
          v-for="experiment in unpublished_experiments"
          :key="experiment.code"
          class="d-flex justify-content-between align-items-center"
        >
          {{ experiment.name }} ({{ experiment.code }})
          <span>
            <a :href="`/profile/experiment/edit/${experiment.code}`"> Edit </a>
            |
            <a href="#" @click="$emit('delete-experiment', experiment.code)">
              Delete
            </a>
            |
            <a href="#" @click="$emit('publish-experiment', experiment.code)">
              Publish
            </a>
            |
            <a :href="`/test_experiment/${experiment.code}`">Test Experiment</a>
            |
            <a :href="'/raw_data/?code=' + experiment.code"
              >Download raw data</a
            >
            |
            <a :href="'/processed_data/?code=' + experiment.code">
              Download processed data</a
            >
            <b-badge
              variant="primary"
              pill
              v-b-tooltip.hover
              :title="experiment.responses + ' responses'"
              >{{ experiment.responses }}</b-badge
            >
          </span>
          <!-- Missing a button to publish, to edit, view and to delete -->
        </b-list-group-item>
      </b-list-group>
    </template>
    <br />
    <template v-if="published_experiments.length > 0">
      <h4>Published experiments:</h4>
      <b-list-group class="col">
        <b-list-group-item
          v-for="experiment in published_experiments"
          :key="experiment.code"
          class="d-flex justify-content-between align-items-center"
        >
          {{ experiment.name }} ({{ experiment.code }}) ({{
            experiment.enabled ? "enabled" : "disabled"
          }})
          <span>
            <a :href="`/profile/experiment/edit/${experiment.code}`"> View </a>
            |
            <a
              v-if="experiment.enabled"
              href="#"
              @click="$emit('disable-experiment', experiment.code)"
              >Disable
            </a>
            <a
              v-else
              href="#"
              @click="$emit('enable-experiment', experiment.code)"
              >Enable
            </a>
            |
            <a href="#" @click="$emit('delete-experiment', experiment.code)">
              Delete
            </a>
            |
            <a :href="'/prep_screen/?code=' + experiment.code">Do Experiment</a>
            |
            <a :href="'/raw_data/?code=' + experiment.code"
              >Download raw data</a
            >
            |
            <a :href="'/processed_data/?code=' + experiment.code">
              Download processed data</a
            >
            <b-badge
              variant="primary"
              pill
              v-b-tooltip.hover
              :title="experiment.responses + ' responses'"
              >{{ experiment.responses }}</b-badge
            >
          </span>
          <!-- Missing a button to publish, to edit, view and to delete -->
        </b-list-group-item>
      </b-list-group>
    </template>
    <br />
    <a href="/profile/create_experiment" class="btn btn-primary"
      >Create Experiment</a
    >
    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {};
  },
  props: {
    current_user: Object,
    experiments: Array,
  },
  mounted: function () {},
  components: {},
  computed: {
    published_experiments() {
      return this.experiments.filter((e) => e.published);
    },
    unpublished_experiments() {
      return this.experiments.filter((e) => !e.published);
    },
    isUserEmpty() {
      return (
        Object.keys(this.current_user).length === 0 &&
        this.current_user.constructor === Object
      );
    },
  },
  watch: {},
  methods: {
    isObjectEmpty: function (obj) {
      return Object.keys(obj).length === 0 && obj.constructor === Object;
    },
  },
};
</script>

<style scoped></style>
