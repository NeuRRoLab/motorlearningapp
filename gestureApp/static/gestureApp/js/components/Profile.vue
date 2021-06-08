<template>
  <div v-if="!isUserEmpty" class="container-fluid">
    <h1 class="text-center">Profile</h1>
    <a href="/profile/create_study" class="btn btn-lg text-center btn-primary"
      >Create Study</a
    >
    <a
      v-if="studies.length > 0"
      href="/profile/create_experiment"
      class="btn btn-lg text-center btn-primary"
      >Create Experiment</a
    >
    <br />
    <br />
    <!-- Unpublished studies -->
    <template v-if="unpublished_studies.length > 0">
      <h4>Unpublished studies:</h4>
      <div
        class="row mt-3"
        v-for="study in unpublished_studies"
        :key="study.code"
      >
        <b-card-group class="col">
          <b-card :header="`${study.name} (${study.code})`">
            <p v-if="study.description !== ''">{{ study.description }}</p>
            <p class="card-text mt-2">
              Study actions:
              <a :href="`/profile/study/edit/${study.code}`"> Edit </a>
              |
              <a href="#" @click="$emit('delete-study', study.code)">
                Delete
              </a>
              |
              <a href="#" @click="$emit('duplicate-study', study.code)">
                Duplicate
              </a>
              |
              <a href="#" @click="$emit('publish-study', study.code)">
                Publish
              </a>
            </p>
            <h6>New group</h6>
            <b-form inline>
              <b-form-input
                id="inline-form-input-name"
                v-model="group_name"
                class="mb-2 mr-sm-2 mb-sm-0"
                placeholder="Group name"
              ></b-form-input>
              <b-button
                variant="primary"
                @click="
                  $emit('new-group', group_name, study.code);
                  group_name = null;
                "
                >Save</b-button
              >
            </b-form>
            <br />
            <h5>Experiments</h5>
            <b-list-group v-if="study.experiments.length > 0">
              <b-list-group-item
                v-for="experiment in study.experiments"
                :key="'E' + experiment.code"
                class="d-flex justify-content-between align-items-center"
                >{{ experiment.name }} ({{ experiment.code }})
                <span>
                  <a :href="`/profile/experiment/edit/${experiment.code}`">
                    Edit
                  </a>
                  |
                  <a
                    href="#"
                    @click="$emit('delete-experiment', experiment.code)"
                  >
                    Delete
                  </a>
                  |
                  <a
                    href="#"
                    @click="$emit('duplicate-experiment', experiment.code)"
                  >
                    Duplicate
                  </a>
                  |
                  <a :href="`/experiment/${experiment.code}`"
                    >Test Experiment</a
                  >
                  |
                  <a :href="'/raw_data/?code=' + experiment.code">Raw data</a>
                  |
                  <a :href="'/processed_data/?code=' + experiment.code">
                    Processed data</a
                  >
                  |
                  <a
                    :href="
                      '/api/experiment/download_end_survey/' + experiment.code
                    "
                  >
                    Survey data</a
                  >
                  |
                  <a :href="'/api/experiment/cohen_metrics/' + experiment.code">
                    Cohen metrics</a
                  >
                  <b-badge
                    variant="primary"
                    pill
                    v-b-tooltip.hover
                    :title="experiment.responses + ' responses'"
                    >{{ experiment.responses }}</b-badge
                  >
                </span></b-list-group-item
              >
            </b-list-group>
            <p v-else>No experiments in this study.</p>
          </b-card>
        </b-card-group>
      </div>
    </template>
    <br />
    <!-- Published Studies -->
    <template v-if="published_studies.length > 0">
      <h4>Published studies:</h4>
      <div
        class="row mt-3"
        v-for="study in published_studies"
        :key="study.code"
      >
        <b-card-group class="col">
          <b-card
            :header="`${study.name} (${study.code}) (${
              study.enabled ? 'enabled' : 'disabled'
            })`"
          >
            <p v-if="study.description !== ''">{{ study.description }}</p>
            <p class="card-text mt-2">
              Study actions:
              <a :href="`/profile/study/edit/${study.code}`"> View </a>
              |
              <a href="#" @click="$emit('delete-study', study.code)">
                Delete
              </a>
              |
              <a href="#" @click="$emit('duplicate-study', study.code)">
                Duplicate
              </a>
              |
              <a
                v-if="study.enabled"
                href="#"
                @click="$emit('disable-study', study.code)"
                >Disable
              </a>
              <a v-else href="#" @click="$emit('enable-study', study.code)"
                >Enable
              </a>
            </p>
            <h5>Experiments</h5>
            <b-list-group v-if="study.experiments.length > 0">
              <b-list-group-item
                v-for="experiment in study.experiments"
                :key="'E' + experiment.code"
                class="d-flex justify-content-between align-items-center"
                >{{ experiment.name }} ({{ experiment.code }}) ({{
                  experiment.enabled ? "enabled" : "disabled"
                }})
                <span>
                  <a :href="`/profile/experiment/edit/${experiment.code}`">
                    View
                  </a>
                  |
                  <a
                    href="#"
                    @click="$emit('delete-experiment', experiment.code)"
                  >
                    Delete
                  </a>
                  |
                  <a
                    href="#"
                    @click="$emit('duplicate-experiment', experiment.code)"
                  >
                    Duplicate
                  </a>
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
                  <a :href="`/experiment/${experiment.code}`">Do Experiment</a>
                  |
                  <a :href="'/raw_data/?code=' + experiment.code">Raw data</a>
                  |
                  <a :href="'/processed_data/?code=' + experiment.code">
                    Processed data</a
                  >
                  |
                  <a
                    :href="
                      '/api/experiment/download_end_survey/' + experiment.code
                    "
                  >
                    Survey data</a
                  >
                  |
                  <a :href="'/api/experiment/cohen_metrics/' + experiment.code">
                    Cohen metrics</a
                  >
                  <b-badge
                    variant="primary"
                    pill
                    v-b-tooltip.hover
                    :title="experiment.responses + ' responses'"
                    >{{ experiment.responses }}</b-badge
                  >
                </span></b-list-group-item
              >
            </b-list-group>
            <p v-else>No experiments in this study.</p>
          </b-card>
        </b-card-group>
      </div>
    </template>
    <br />

    <br />
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      group_name: null,
    };
  },
  props: {
    current_user: Object,
    studies: Array,
  },
  mounted: function () {},
  components: {},
  computed: {
    published_studies() {
      return this.studies.filter((s) => s.published);
    },
    unpublished_studies() {
      return this.studies.filter((s) => !s.published);
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
