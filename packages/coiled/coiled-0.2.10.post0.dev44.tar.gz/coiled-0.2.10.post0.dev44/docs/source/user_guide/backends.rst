Configure Your Cloud Provider
=============================

.. toctree::
   :maxdepth: 1
   :hidden:

   aws_configure
   gcp_configure

You can run Coiled on from your own AWS or GCP account.
This allows you to make use of security/data access controls, compliance standards,
and promotional credits that you already have in place.

.. panels::
   :card: border-0
   :container: container-lg pb-3
   :column: col-md-6 col-md-6 p-2
   :body: text-center border-0
   :header: text-center border-0 h4 bg-white
   :footer: border-0 bg-white

   Use Coiled with AWS
   ^^^^^^^^^^^^^^^^^^^

   .. figure:: images/logo-aws.png
      :width: 35%
      :alt: Use Coiled with Amazon Web Services (AWS)

   +++

   .. link-button:: aws_configure
      :type: ref
      :text: Configure your AWS account
      :classes: btn-full btn-block stretched-link

   ---


   Use Coiled with GCP
   ^^^^^^^^^^^^^^^^^^^

   .. figure:: images/logo-gcp.png
      :width: 100%
      :alt: Use Coiled with Google Cloud Platform (GCP)

   +++

   .. link-button:: gcp_configure
      :type: ref
      :text: Configure your GCP account
      :classes: btn-full btn-block stretched-link

Coiled is only responsible for provisioning resources for
clusters you create. Once a Dask cluster is created, all computations,
data transfer, and client-to-scheduler communication occurs entirely
within your cloud provider account.

.. figure:: images/backend-external-aws-vm.png
   :width: 100%

.. _no-cloud-provider:

Need a cloud provider account?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. panels::
   :card: border-0
   :container: container-lg pb-3
   :column: col-md-6 col-md-6 p-2
   :body: text-center border-0
   :header: text-center border-0 h4 bg-white
   :footer: border-0 bg-white

   .. figure:: images/logo-aws.png
      :width: 35%
      :alt: Sign up for Amazon Web Services (AWS)

   +++

   .. link-button:: https://aws.amazon.com/free
      :text: Sign up for AWS Free Tier
      :classes: btn-full btn-block stretched-link

   ---


   .. figure:: images/logo-gcp.png
      :width: 100%
      :alt: Sign up for Google Cloud Free Tier

   +++

   .. link-button:: https://cloud.google.com/free
      :text: Sign up for Google Cloud Free Tier
      :classes: btn-full btn-block stretched-link
